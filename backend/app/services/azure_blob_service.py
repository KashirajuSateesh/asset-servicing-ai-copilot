from azure.storage.blob import BlobServiceClient

from app.config import settings


def get_blob_service_client() -> BlobServiceClient:
    if not settings.azure_storage_connection_string:
        raise ValueError("Azure Storage connection string is missing.")

    return BlobServiceClient.from_connection_string(
        settings.azure_storage_connection_string
    )


def list_blobs_in_container(container_name: str) -> list[dict]:
    blob_service_client = get_blob_service_client()
    container_client = blob_service_client.get_container_client(container_name)

    blobs = []

    for blob in container_client.list_blobs():
        blobs.append(
            {
                "name": blob.name,
                "container": container_name,
                "size": blob.size,
                "last_modified": blob.last_modified.isoformat()
                if blob.last_modified
                else None,
            }
        )

    return blobs