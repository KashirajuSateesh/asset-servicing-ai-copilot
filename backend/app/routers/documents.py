from fastapi import APIRouter, HTTPException

from app.services.azure_blob_service import list_blobs_in_container
from app.services.pdf_extraction_service import extract_pdf_pages_from_blob
from app.services.chunking_service import create_chunks_from_pdf_pages

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