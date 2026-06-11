import fitz

from app.services.azure_blob_service import get_blob_service_client


def extract_pdf_pages_from_blob(container_name: str, blob_name: str) -> list[dict]:
    blob_service_client = get_blob_service_client()
    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_name,
    )

    pdf_bytes = blob_client.download_blob().readall()

    document = fitz.open(stream=pdf_bytes, filetype="pdf")

    pages = []

    for page_index, page in enumerate(document, start=1):
        text = page.get_text("text").strip()

        pages.append(
            {
                "page_number": page_index,
                "text": text,
                "char_count": len(text),
            }
        )

    document.close()

    return pages