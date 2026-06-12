from openai import OpenAI

from app.config import settings
from app.services.azure_search_service import hybrid_search_policy_chunks
from app.services.domain_classifier_service import detect_business_domain


CHAT_MODEL = "gpt-4o-mini"


def get_openai_chat_client() -> OpenAI:
    """
    Creates an OpenAI client for answer generation.

    We already use OpenAI for embeddings.
    This client will be used for the chat/answer generation part of RAG.
    """

    if not settings.openai_api_key:
        raise ValueError("OpenAI API key is missing.")

    return OpenAI(api_key=settings.openai_api_key)


def build_context_from_chunks(chunks: list[dict]) -> str:
    """
    Converts retrieved search chunks into a clean context block for the LLM.

    Why this is needed:
    The LLM should not answer from memory.
    It should answer only using the chunks retrieved from Azure AI Search.

    Each chunk includes citation metadata:
    - document name
    - page number
    - chunk number
    """

    context_parts = []

    for index, chunk in enumerate(chunks, start=1):
        citation_label = f"[Source {index}]"

        context_parts.append(
            f"{citation_label}\n"
            f"Document: {chunk.get('document_name')}\n"
            f"Page: {chunk.get('page_number')}\n"
            f"Chunk: {chunk.get('chunk_index')}\n"
            f"Business Domain: {chunk.get('business_domain')}\n"
            f"Text:\n{chunk.get('chunk_text')}\n"
        )

    return "\n---\n".join(context_parts)


def build_citations(chunks: list[dict]) -> list[dict]:
    """
    Creates a clean citations list from retrieved chunks.

    This will be returned to the frontend/API response so the user can see
    which document sections were used to generate the answer.
    """

    citations = []

    for index, chunk in enumerate(chunks, start=1):
        citations.append(
            {
                "source_number": index,
                "document_name": chunk.get("document_name"),
                "page_number": chunk.get("page_number"),
                "chunk_index": chunk.get("chunk_index"),
                "business_domain": chunk.get("business_domain"),
                "source_blob_name": chunk.get("source_blob_name"),
                "score": chunk.get("score"),
            }
        )

    return citations


def generate_answer_from_context(query: str, context: str) -> str:
    """
    Generates a final answer using the retrieved context.

    Important rule:
    The model must answer only from the provided context.
    If the context does not contain enough information, it should say that.
    This reduces hallucination.
    """

    client = get_openai_chat_client()

    system_prompt = """
You are an enterprise asset servicing AI copilot.

Your job is to answer user questions using only the provided source context.

Rules:
1. Do not use outside knowledge.
2. If the answer is not present in the context, say you do not have enough information.
3. Keep the answer clear and business-friendly.
4. Include citation references like [Source 1], [Source 2] when using information.
5. Do not expose restricted account data unless it is provided in the context.
6. If the question involves escalation, SLA, evidence, or operational thresholds, be specific.
"""

    user_prompt = f"""
User question:
{query}

Source context:
{context}

Generate the final answer using only the source context.
"""

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    return response.choices[0].message.content


def calculate_confidence_score(chunks: list[dict]) -> dict:
    """
    Calculates a simple confidence score based on retrieved search results.

    Why we need this:
    In a RAG system, not every answer should be treated equally.
    If retrieval quality is weak, the copilot should show lower confidence
    and later route the case to human review.

    Current simple logic:
    - Use the top retrieved score from Azure AI Search.
    - Normalize it into a 0 to 1 confidence value.
    - Assign a confidence label.

    Note:
    Azure AI Search scores differ between keyword, vector, and hybrid search.
    This is a demo-level confidence score. Later, we can improve it with
    reranking, citation coverage, and LLM self-evaluation.
    """

    if not chunks:
        return {
            "confidence_score": 0.0,
            "confidence_label": "low",
            "human_review_required": True,
        }

    # Get the highest search score from retrieved chunks.
    top_score = chunks[0].get("score") or 0.0

    # Hybrid search scores are usually small decimals.
    # This simple normalization keeps the score between 0 and 1.
    normalized_score = min(float(top_score) / 0.03, 1.0)

    if normalized_score >= 0.75:
        confidence_label = "high"
        human_review_required = False
    elif normalized_score >= 0.50:
        confidence_label = "medium"
        human_review_required = False
    else:
        confidence_label = "low"
        human_review_required = True

    return {
        "confidence_score": round(normalized_score, 2),
        "confidence_label": confidence_label,
        "human_review_required": human_review_required,
    }


def generate_rag_answer(
    query: str,
    top_k: int = 5,
    business_domain: str | None = None,
) -> dict:
    """
    Full RAG pipeline for policy/SOP questions.

    This function connects retrieval and answer generation:

    1. Runs hybrid search against Azure AI Search.
    2. Optionally filters by business domain.
    3. Builds source context from retrieved chunks.
    4. Sends context + question to OpenAI.
    5. Returns final answer with citations.

    business_domain is optional.

    Example:
    - settlement
    - reconciliation
    - custody
    - corporate_actions
    - sla_escalation
    """

    # Step 1: Detect business domain if the user/API did not provide one.
    # Example:
    # "failed settlement escalation" -> settlement
    # "cash reconciliation break" -> reconciliation
    detected_business_domain = business_domain

    if not detected_business_domain:
        detected_business_domain = detect_business_domain(query)

    # Step 2: Retrieve relevant policy/SOP chunks using hybrid search.
    # If a domain is detected, Azure AI Search will only search that domain.
    retrieved_chunks = hybrid_search_policy_chunks(
        query=query,
        top_k=top_k,
        business_domain=detected_business_domain,
    )

    # Step 2: If no chunks are found, return a safe response.
    if not retrieved_chunks:
        return {
            "query": query,
            "business_domain": detected_business_domain,
            "answer": "I could not find relevant policy or SOP content for this question.",
            "retrieved_chunk_count": 0,
            "confidence_score": 0.0,
            "confidence_label": "low",
            "human_review_required": True,
            "citations": [],
        }

    # Step 3: Convert retrieved chunks into an LLM-ready context block.
    context = build_context_from_chunks(retrieved_chunks)

    # Step 4: Generate final answer using only the retrieved context.
    answer = generate_answer_from_context(
        query=query,
        context=context,
    )

    # Step 5: Build citation metadata for traceability.
    citations = build_citations(retrieved_chunks)

    # Step 6: Calculate confidence score from retrieval quality.
    confidence = calculate_confidence_score(retrieved_chunks)

    return {
        "query": query,
        "business_domain": detected_business_domain,
        "answer": answer,
        "retrieved_chunk_count": len(retrieved_chunks),
        "confidence_score": confidence["confidence_score"],
        "confidence_label": confidence["confidence_label"],
        "human_review_required": confidence["human_review_required"],
        "citations": citations,
    }