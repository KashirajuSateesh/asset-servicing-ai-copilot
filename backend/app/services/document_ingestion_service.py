from app.services.pdf_extraction_service import extract_pdf_pages_from_blob
from app.services.chunking_service import create_chunks_from_pdf_pages
from app.services.embedding_service import generate_embeddings_for_chunks
from app.services.azure_search_service import upload_chunks_to_search_index


def ingest_single_pdf(blob_name: str) -> dict:
    """
    Ingests one PDF from Azure Blob into Azure AI Search.

    This is the reusable ingestion pipeline.

    What this function does:
    1. Reads the PDF from the raw-pdfs Blob container.
    2. Extracts page text from the PDF.
    3. Splits the text into chunks.
    4. Creates embeddings for each chunk.
    5. Uploads the chunks and embeddings into Azure AI Search.

    Both single-file ingestion and bulk ingestion should use this function.
    """

    # Step 1: Extract text page by page from the PDF stored in Azure Blob.
    pages = extract_pdf_pages_from_blob(
        container_name="raw-pdfs",
        blob_name=blob_name,
    )

    # Step 2: Convert extracted page text into smaller metadata-rich chunks.
    chunks = create_chunks_from_pdf_pages(
        document_name=blob_name,
        pages=pages,
    )

    # Step 3: Generate OpenAI embeddings for every chunk.
    embedded_chunks = generate_embeddings_for_chunks(chunks)

    # Step 4: Upload embedded chunks into Azure AI Search.
    upload_result = upload_chunks_to_search_index(embedded_chunks)

    return {
        "blob_name": blob_name,
        "pages_extracted": len(pages),
        "chunks_created": len(chunks),
        "search_upload_result": upload_result,
    }