import re
from hashlib import sha256


def infer_business_domain(document_name: str) -> str:
    name = document_name.lower()

    if "settlement" in name or "exception" in name:
        return "settlement"
    if "reconciliation" in name:
        return "reconciliation"
    if "corporate_actions" in name or "corporate" in name:
        return "corporate_actions"
    if "custody" in name:
        return "custody"
    if "sla" in name or "escalation" in name:
        return "sla_escalation"

    return "general"


def infer_document_type(document_name: str) -> str:
    name = document_name.lower()

    if "sop" in name:
        return "sop"
    if "policy" in name:
        return "policy"
    if "procedure" in name:
        return "procedure"
    if "guide" in name:
        return "guide"
    if "standard" in name:
        return "standard"

    return "document"


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_text_into_chunks(
    text: str,
    max_chars: int = 1200,
    overlap_chars: int = 150,
) -> list[str]:
    text = clean_text(text)

    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]

        last_period = chunk.rfind(".")
        if last_period > int(max_chars * 0.6):
            chunk = chunk[: last_period + 1]
            end = start + last_period + 1

        chunks.append(chunk.strip())

        start = max(end - overlap_chars, end)

    return chunks


def create_chunk_id(document_name: str, page_number: int, chunk_index: int, chunk_text: str) -> str:
    raw_value = f"{document_name}|{page_number}|{chunk_index}|{chunk_text[:100]}"
    return sha256(raw_value.encode("utf-8")).hexdigest()


def create_chunks_from_pdf_pages(
    document_name: str,
    pages: list[dict],
) -> list[dict]:
    all_chunks = []

    business_domain = infer_business_domain(document_name)
    document_type = infer_document_type(document_name)

    for page in pages:
        page_number = page["page_number"]
        page_text = page["text"]

        text_chunks = split_text_into_chunks(page_text)

        for chunk_index, chunk_text in enumerate(text_chunks, start=1):
            chunk_id = create_chunk_id(
                document_name=document_name,
                page_number=page_number,
                chunk_index=chunk_index,
                chunk_text=chunk_text,
            )

            all_chunks.append(
                {
                    "chunk_id": chunk_id,
                    "document_name": document_name,
                    "document_type": document_type,
                    "business_domain": business_domain,
                    "page_number": page_number,
                    "chunk_index": chunk_index,
                    "chunk_text": chunk_text,
                    "char_count": len(chunk_text),
                    "source_container": "raw-pdfs",
                    "source_blob_name": document_name,
                }
            )

    return all_chunks