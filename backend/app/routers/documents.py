from fastapi import APIRouter, HTTPException

from app.services.azure_blob_service import list_blobs_in_container
from app.services.pdf_extraction_service import extract_pdf_pages_from_blob
from app.services.chunking_service import create_chunks_from_pdf_pages
from app.services.embedding_service import generate_embedding, generate_embeddings_for_chunks
from app.services.azure_search_service import (
    create_policy_chunks_index,
    search_policy_chunks,
    upload_chunks_to_search_index,
    vector_search_policy_chunks,
    hybrid_search_policy_chunks,
)
from app.services.rag_answer_service import generate_rag_answer

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


ALLOWED_CONTAINERS = {
    "raw-pdfs",
    "raw-json",
    "raw-csv",
    "raw-excel",
    "processed",
    "ingestion-logs",
}


@router.get("/blobs/{container_name}")
def list_container_blobs(container_name: str):
    if container_name not in ALLOWED_CONTAINERS:
        raise HTTPException(
            status_code=400,
            detail=f"Container '{container_name}' is not allowed.",
        )

    try:
        blobs = list_blobs_in_container(container_name)
        return {
            "container": container_name,
            "count": len(blobs),
            "blobs": blobs,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list blobs from container '{container_name}': {str(exc)}",
        )
    
@router.get("/pdf-preview/{blob_name}")
def preview_pdf_text(blob_name: str):
    try:
        pages = extract_pdf_pages_from_blob(
            container_name="raw-pdfs",
            blob_name=blob_name,
        )

        preview_pages = pages[:3]

        return {
            "blob_name": blob_name,
            "total_pages": len(pages),
            "preview_pages": preview_pages,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract PDF text from '{blob_name}': {str(exc)}",
        )
    
@router.get("/pdf-chunks-preview/{blob_name}")
def preview_pdf_chunks(blob_name: str):
    try:
        pages = extract_pdf_pages_from_blob(
            container_name="raw-pdfs",
            blob_name=blob_name,
        )

        chunks = create_chunks_from_pdf_pages(
            document_name=blob_name,
            pages=pages,
        )

        return {
            "blob_name": blob_name,
            "total_chunks": len(chunks),
            "preview_chunks": chunks[:3],
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create chunks from '{blob_name}': {str(exc)}",
        )
    

@router.get("/embedding-preview/{blob_name}")
def preview_embedding(blob_name: str):
    """
    Extracts one PDF from Azure Blob, creates chunks, and generates an embedding
    for only the first chunk. This is only for testing the OpenAI embedding flow.
    """

    try:
        # Step 1: Extract PDF pages from Azure Blob
        pages = extract_pdf_pages_from_blob(
            container_name="raw-pdfs",
            blob_name=blob_name,
        )

        # Step 2: Convert extracted pages into metadata-rich chunks
        chunks = create_chunks_from_pdf_pages(
            document_name=blob_name,
            pages=pages,
        )

        # Step 3: If no chunks are created, return a helpful response
        if not chunks:
            return {
                "blob_name": blob_name,
                "message": "No chunks found for this PDF.",
            }

        # Step 4: Take only the first chunk to reduce OpenAI token usage
        first_chunk = chunks[0]

        # Step 5: Generate embedding for the first chunk
        embedding = generate_embedding(first_chunk["chunk_text"])

        # Step 6: Return metadata and embedding size, not the full embedding vector
        return {
            "blob_name": blob_name,
            "chunk_id": first_chunk["chunk_id"],
            "document_type": first_chunk["document_type"],
            "business_domain": first_chunk["business_domain"],
            "page_number": first_chunk["page_number"],
            "chunk_char_count": first_chunk["char_count"],
            "embedding_dimension": len(embedding),
            "embedding_preview": embedding[:5],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate embedding preview for '{blob_name}': {str(exc)}",
        )
    

@router.post("/search-index/create")
def create_search_index():
    """
    Creates or updates the Azure AI Search index used to store
    PDF chunks, metadata, citations, and embeddings.
    """

    try:
        result = create_policy_chunks_index()
        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create Azure AI Search index: {str(exc)}",
        )
    

@router.post("/ingest-pdf/{blob_name}")
def ingest_single_pdf(blob_name: str):
    """
    Ingests one PDF from Azure Blob into Azure AI Search.

    Flow:
    1. Read PDF from raw-pdfs container
    2. Extract page-level text
    3. Create metadata-rich chunks
    4. Generate OpenAI embeddings
    5. Upload chunks to Azure AI Search
    """

    try:
        # Step 1: Extract PDF text from Azure Blob
        pages = extract_pdf_pages_from_blob(
            container_name="raw-pdfs",
            blob_name=blob_name,
        )

        # Step 2: Create chunks with citation metadata
        chunks = create_chunks_from_pdf_pages(
            document_name=blob_name,
            pages=pages,
        )

        # Step 3: Generate embeddings for each chunk
        embedded_chunks = generate_embeddings_for_chunks(chunks)

        # Step 4: Upload embedded chunks to Azure AI Search
        upload_result = upload_chunks_to_search_index(embedded_chunks)

        return {
            "blob_name": blob_name,
            "pages_extracted": len(pages),
            "chunks_created": len(chunks),
            "search_upload_result": upload_result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest PDF '{blob_name}': {str(exc)}",
        )
    

@router.get("/search")
def search_documents(query: str, top_k: int = 5):
    """
    Searches indexed PDF chunks from Azure AI Search.

    For now, this uses keyword search.
    Later, we will upgrade it to hybrid search using:
    - keyword search
    - vector search
    - metadata filters
    """

    try:
        # Search indexed policy/SOP chunks using the user's query.
        results = search_policy_chunks(
            query=query,
            top_k=top_k,
        )

        return {
            "query": query,
            "top_k": top_k,
            "result_count": len(results),
            "results": results,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search documents: {str(exc)}",
        )
    
@router.get("/vector-search")
def vector_search_documents(query: str, top_k: int = 5):
    """
    Searches indexed PDF chunks using vector similarity.

    What this endpoint does:
    1. Takes the user's question.
    2. Converts the question into an embedding using OpenAI.
    3. Searches Azure AI Search using vector similarity.
    4. Returns chunks that are semantically close to the question.

    This is better than keyword search when the user asks a question
    using different words than the PDF.
    """

    try:
        # Run vector search against Azure AI Search.
        results = vector_search_policy_chunks(
            query=query,
            top_k=top_k,
        )

        return {
            "query": query,
            "search_type": "vector",
            "top_k": top_k,
            "result_count": len(results),
            "results": results,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run vector search: {str(exc)}",
        )
    
@router.get("/hybrid-search")
def hybrid_search_documents(query: str, top_k: int = 5):
    """
    Searches indexed PDF chunks using hybrid search.

    What this endpoint does:
    1. Takes the user's question.
    2. Runs keyword search using the query text.
    3. Runs vector search using the query embedding.
    4. Combines both signals inside Azure AI Search.
    5. Returns the best chunks for RAG answer generation.

    This will become the main retrieval endpoint for the copilot.
    """

    try:
        # Run hybrid search against Azure AI Search.
        results = hybrid_search_policy_chunks(
            query=query,
            top_k=top_k,
        )

        return {
            "query": query,
            "search_type": "hybrid",
            "top_k": top_k,
            "result_count": len(results),
            "results": results,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run hybrid search: {str(exc)}",
        )
    

@router.post("/ingest-all-pdfs")
def ingest_all_pdfs():
    """
    Ingests all PDFs from the raw-pdfs Azure Blob container into Azure AI Search.

    What this endpoint does:
    1. Lists all PDF files from the raw-pdfs container.
    2. For each PDF:
       - extracts text
       - creates chunks
       - generates embeddings
       - uploads chunks to Azure AI Search
    3. Returns a summary of how many PDFs were processed.

    Why this is useful:
    This turns our one-file test pipeline into a full document ingestion pipeline.
    """

    try:
        # Step 1: Get all blobs from the raw-pdfs container.
        blobs = list_blobs_in_container("raw-pdfs")

        ingestion_results = []

        # Step 2: Process each PDF one by one.
        for blob in blobs:
            blob_name = blob["name"]

            # Extract page text from Azure Blob PDF.
            pages = extract_pdf_pages_from_blob(
                container_name="raw-pdfs",
                blob_name=blob_name,
            )

            # Create metadata-rich chunks from extracted pages.
            chunks = create_chunks_from_pdf_pages(
                document_name=blob_name,
                pages=pages,
            )

            # Generate embeddings for every chunk.
            embedded_chunks = generate_embeddings_for_chunks(chunks)

            # Upload chunks to Azure AI Search.
            upload_result = upload_chunks_to_search_index(embedded_chunks)

            ingestion_results.append(
                {
                    "blob_name": blob_name,
                    "pages_extracted": len(pages),
                    "chunks_created": len(chunks),
                    "uploaded_count": upload_result["uploaded_count"],
                    "failed_count": upload_result["failed_count"],
                }
            )

        return {
            "total_pdfs_found": len(blobs),
            "total_pdfs_processed": len(ingestion_results),
            "results": ingestion_results,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest all PDFs: {str(exc)}",
        )
    
@router.get("/ask")
def ask_documents(
    query: str,
    top_k: int = 5,
    business_domain: str | None = None,
):
    """
    Generates a RAG answer from indexed policy/SOP documents.

    What this endpoint does:
    1. Takes the user's question.
    2. Optionally applies a business domain filter.
    3. Runs hybrid search to retrieve relevant PDF chunks.
    4. Sends the retrieved chunks to OpenAI.
    5. Generates a business-friendly answer.
    6. Returns the answer with citation metadata.

    Example business_domain values:
    - settlement
    - reconciliation
    - custody
    - corporate_actions
    - sla_escalation
    """

    try:
        # Keep top_k controlled so we do not send too much context to the LLM.
        if top_k < 1 or top_k > 10:
            raise HTTPException(
                status_code=400,
                detail="top_k must be between 1 and 10.",
            )

        # Run the full RAG pipeline with optional metadata filtering.
        rag_response = generate_rag_answer(
            query=query,
            top_k=top_k,
            business_domain=business_domain,
        )

        return rag_response

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate RAG answer: {str(exc)}",
        )