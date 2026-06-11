from azure.core.credentials import AzureKeyCredential
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

from app.config import settings
from azure.search.documents import SearchClient


def get_search_index_client() -> SearchIndexClient:
    """
    Creates an Azure AI Search index client.
    This client is used for index-level operations like creating or deleting indexes.
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
    - deleting chunks
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
    Creates the Azure AI Search index used for PDF policy/SOP chunks.

    The index stores:
    - chunk text
    - document metadata
    - OpenAI embedding vector
    - source/citation information
    """

    index_client = get_search_index_client()
    index_name = settings.azure_search_index_name

    fields = [
        # Unique key for every chunk
        SimpleField(
            name="chunk_id",
            type=SearchFieldDataType.String,
            key=True,
            filterable=True,
        ),

        # Searchable document metadata
        SearchableField(
            name="document_name",
            type=SearchFieldDataType.String,
            filterable=True,
            sortable=True,
        ),
        SimpleField(
            name="document_type",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SimpleField(
            name="business_domain",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),

        # Citation metadata
        SimpleField(
            name="page_number",
            type=SearchFieldDataType.Int32,
            filterable=True,
            sortable=True,
        ),
        SimpleField(
            name="chunk_index",
            type=SearchFieldDataType.Int32,
            filterable=True,
            sortable=True,
        ),

        # Main searchable text
        SearchableField(
            name="chunk_text",
            type=SearchFieldDataType.String,
            analyzer_name="en.microsoft",
        ),

        # Source tracking
        SimpleField(
            name="source_container",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
        SimpleField(
            name="source_blob_name",
            type=SearchFieldDataType.String,
            filterable=True,
        ),

        # OpenAI embedding vector.
        # text-embedding-3-small returns 1536 dimensions.
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="policy-vector-profile",
        ),

        # Embedding model used for traceability
        SimpleField(
            name="embedding_model",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
    ]

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

    # Create or update allows us to rerun this safely during development.
    index_client.create_or_update_index(index)

    return {
        "index_name": index_name,
        "status": "created_or_updated",
        "embedding_dimensions": 1536,
    }

def upload_chunks_to_search_index(chunks: list[dict]) -> dict:
    """
    Uploads embedded PDF chunks into Azure AI Search.

    Each chunk should already contain:
    - chunk metadata
    - chunk text
    - embedding vector
    - citation/source information
    """

    if not chunks:
        return {
            "status": "skipped",
            "message": "No chunks were provided.",
            "uploaded_count": 0,
        }

    search_client = get_search_client()

    # Azure AI Search expects a list of dictionaries where keys match index fields.
    documents = []

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

    # upload_documents performs an upsert-like operation for matching document keys.
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

    This is the first search version.
    Later we will upgrade it to hybrid search:
    - keyword search
    - vector search
    - metadata filtering
    """

    search_client = get_search_client()

    # Search Azure AI Search index using the user's query text.
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

    # Convert Azure Search result objects into normal Python dictionaries.
    chunks = []

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