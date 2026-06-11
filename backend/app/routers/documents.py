from fastapi import APIRouter, HTTPException

from app.services.azure_blob_service import list_blobs_in_container

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