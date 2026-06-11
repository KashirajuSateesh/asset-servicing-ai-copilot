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