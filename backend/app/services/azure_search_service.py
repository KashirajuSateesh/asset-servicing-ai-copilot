from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery

from app.config import settings
from app.services.embedding_service import generate_embedding


def get_search_index_client() -> SearchIndexClient:
    """
    Creates an Azure AI Search index client.

    This client is used for index-level operations like:
    - creating indexes
    - updating indexes
    - deleting indexes

    We use this when setting up the vector database structure.
    """

    if not settings.azure_search_endpoint or not settings.azure_search_key:
        raise ValueError("Azure AI Search endpoint or key is missing.")

    return SearchIndexClient(
        endpoint=settings.azure_search_endpoint,
        credential=AzureKeyCredential(settings.azure_search_key),
    )


def get_search_client() -> SearchClient:
    """
    Creates an Azure AI Search document client.

    This client is used for document-level operations like:
    - uploading chunks
    - searching chunks
    - retrieving indexed data

    We use this after the index already exists.
    """

    if not settings.azure_search_endpoint or not settings.azure_search_key:
        raise ValueError("Azure AI Search endpoint or key is missing.")

    return SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index_name,
        credential=AzureKeyCredential(settings.azure_search_key),
    )


def create_policy_chunks_index() -> dict:
    """
    Creates or updates the Azure AI Search index used for PDF policy/SOP chunks.

    This index works like our vector database.

    It stores:
    - chunk text
    - document metadata
    - page number for citation
    - source blob name
    - OpenAI embedding vector

    The embedding field allows vector search.
    """

    index_client = get_search_index_client()
    index_name = settings.azure_search_index_name

    fields = [
        # Unique ID for every chunk. This is the primary key in Azure AI Search.
        SimpleField(
            name="chunk_id",
            type=SearchFieldDataType.String,
            key=True,
            filterable=True,
        ),

        # Original PDF/document name.
        SearchableField(
            name="document_name",
            type=SearchFieldDataType.String,
            filterable=True,
            sortable=True,
        ),

        # Type of document: sop, policy, procedure, guide, standard.
        SimpleField(
            name="document_type",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),

        # Business domain: settlement, reconciliation, custody, corporate_actions, etc.
        SimpleField(
            name="business_domain",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),

        # Page number helps us create citations in final answers.
        SimpleField(
            name="page_number",
            type=SearchFieldDataType.Int32,
            filterable=True,
            sortable=True,
        ),

        # Chunk number within the page.
        SimpleField(
            name="chunk_index",
            type=SearchFieldDataType.Int32,
            filterable=True,
            sortable=True,
        ),

        # Actual text content from the PDF chunk.
        SearchableField(
            name="chunk_text",
            type=SearchFieldDataType.String,
            analyzer_name="en.microsoft",
        ),

        # Blob container where the original PDF came from.
        SimpleField(
            name="source_container",
            type=SearchFieldDataType.String,
            filterable=True,
        ),

        # Blob filename/source file path.
        SimpleField(
            name="source_blob_name",
            type=SearchFieldDataType.String,
            filterable=True,
        ),

        # OpenAI embedding vector for semantic/vector search.
        # text-embedding-3-small returns 1536-dimensional vectors.
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="policy-vector-profile",
        ),

        # Store embedding model name for traceability.
        SimpleField(
            name="embedding_model",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
    ]

    # HNSW is the approximate nearest neighbor algorithm used for vector search.
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="policy-hnsw-config",
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="policy-vector-profile",
                algorithm_configuration_name="policy-hnsw-config",
            )
        ],
    )

    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search,
    )

    # create_or_update_index lets us safely rerun this during development.
    index_client.create_or_update_index(index)

    return {
        "index_name": index_name,
        "status": "created_or_updated",
        "embedding_dimensions": 1536,
    }


def upload_chunks_to_search_index(chunks: list[dict]) -> dict:
    """
    Uploads embedded PDF chunks into Azure AI Search.

    Input:
    - chunks with metadata
    - chunk text
    - OpenAI embeddings

    Output:
    - upload status
    - uploaded count
    - failed count

    This is the final step of the ingestion pipeline.
    """

    if not chunks:
        return {
            "status": "skipped",
            "message": "No chunks were provided.",
            "uploaded_count": 0,
        }

    search_client = get_search_client()

    documents = []

    # Azure AI Search expects each document to match the index field names.
    for chunk in chunks:
        documents.append(
            {
                "chunk_id": chunk["chunk_id"],
                "document_name": chunk["document_name"],
                "document_type": chunk["document_type"],
                "business_domain": chunk["business_domain"],
                "page_number": chunk["page_number"],
                "chunk_index": chunk["chunk_index"],
                "chunk_text": chunk["chunk_text"],
                "source_container": chunk["source_container"],
                "source_blob_name": chunk["source_blob_name"],
                "embedding": chunk["embedding"],
                "embedding_model": chunk["embedding_model"],
            }
        )

    # Upload documents into Azure AI Search.
    # If a chunk_id already exists, Azure updates/replaces that document.
    result = search_client.upload_documents(documents=documents)

    succeeded = sum(1 for item in result if item.succeeded)
    failed = len(result) - succeeded

    return {
        "status": "completed",
        "uploaded_count": succeeded,
        "failed_count": failed,
        "total_documents": len(documents),
    }


def search_policy_chunks(query: str, top_k: int = 5) -> list[dict]:
    """
    Searches indexed policy/SOP chunks using keyword search.

    What this does:
    1. Takes the user's query as text.
    2. Searches chunk_text and searchable fields in Azure AI Search.
    3. Returns the top matching chunks.

    This is useful when the user query contains exact words from the document.
    Example:
    - "settlement exception SLA"
    """

    search_client = get_search_client()

    results = search_client.search(
        search_text=query,
        top=top_k,
        select=[
            "chunk_id",
            "document_name",
            "document_type",
            "business_domain",
            "page_number",
            "chunk_index",
            "chunk_text",
            "source_blob_name",
        ],
    )

    chunks = []

    # Convert Azure Search result objects into normal dictionaries.
    for result in results:
        chunks.append(
            {
                "score": result.get("@search.score"),
                "chunk_id": result.get("chunk_id"),
                "document_name": result.get("document_name"),
                "document_type": result.get("document_type"),
                "business_domain": result.get("business_domain"),
                "page_number": result.get("page_number"),
                "chunk_index": result.get("chunk_index"),
                "chunk_text": result.get("chunk_text"),
                "source_blob_name": result.get("source_blob_name"),
            }
        )

    return chunks


def vector_search_policy_chunks(query: str, top_k: int = 5) -> list[dict]:
    """
    Searches indexed policy/SOP chunks using vector similarity.

    What this does:
    1. Converts the user's question into an OpenAI embedding.
    2. Sends that query embedding to Azure AI Search.
    3. Azure AI Search compares the query embedding against stored chunk embeddings.
    4. Returns the most semantically similar chunks.

    Why this matters:
    Keyword search only matches exact words.
    Vector search matches meaning.

    Example:
    User asks:
    "When do I need not to escalate a failed settlement?"

    The PDF might say:
    "Critical issues and aged breaks require escalation based on severity and SLA."

    Vector search can still find the right chunk because the meaning is similar.
    """

    search_client = get_search_client()

    # Step 1: Convert the user's query into an embedding vector.
    query_embedding = generate_embedding(query)

    # Step 2: Build vector search query.
    # The field name must match the vector field in our Azure AI Search index.
    vector_query = VectorizedQuery(
        vector=query_embedding,
        k_nearest_neighbors=top_k,
        fields="embedding",
    )

    # Step 3: Run vector search against Azure AI Search.
    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        top=top_k,
        select=[
            "chunk_id",
            "document_name",
            "document_type",
            "business_domain",
            "page_number",
            "chunk_index",
            "chunk_text",
            "source_blob_name",
        ],
    )

    chunks = []

    # Step 4: Convert Azure Search result objects into normal dictionaries.
    for result in results:
        chunks.append(
            {
                "score": result.get("@search.score"),
                "chunk_id": result.get("chunk_id"),
                "document_name": result.get("document_name"),
                "document_type": result.get("document_type"),
                "business_domain": result.get("business_domain"),
                "page_number": result.get("page_number"),
                "chunk_index": result.get("chunk_index"),
                "chunk_text": result.get("chunk_text"),
                "source_blob_name": result.get("source_blob_name"),
            }
        )

    return chunks