from fastapi import APIRouter, HTTPException

from app.services.azure_blob_service import list_blobs_in_container
from app.services.pdf_extraction_service import extract_pdf_pages_from_blob
from app.services.chunking_service import create_chunks_from_pdf_pages
from app.services.embedding_service import generate_embedding

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