import re

from app.services.operational_guidance_service import generate_operational_guidance
from app.services.rag_answer_service import generate_rag_answer


def extract_record_id(query: str) -> str | None:
    """
    Extracts an operational record ID from the user query.

    Why this is useful:
    Users will usually ask natural questions like:
    - "What should I do for EXC-000001?"
    - "Explain trade TRD-0000001"
    - "Check BRK-0000001"

    The orchestrator needs to detect these IDs and route the query to the
    operational guidance flow.
    """

    # Supported record ID formats in our synthetic operational dataset.
    patterns = [
        r"TRD-\d+",
        r"EXC-\d+",
        r"BRK-\d+",
        r"CASE-\d+",
    ]

    query_upper = query.upper()

    for pattern in patterns:
        match = re.search(pattern, query_upper)

        if match:
            return match.group(0)

    return None


def orchestrate_user_query(query: str, top_k: int = 8) -> dict:
    """
    Main orchestration service for the copilot.

    What this function does:
    1. Receives the user's natural language query.
    2. Checks whether the query contains a record ID.
    3. If record ID exists, routes to operational guidance.
    4. If no record ID exists, routes to document RAG.
    5. Returns a consistent response with route information.

    This is the first simple version of the Orchestrator Agent.
    Later, we can extend this with:
    - LLM-based intent classification
    - MCP tool calls
    - Cosmos DB state memory
    - multi-agent routing
    """

    # Step 1: Try to find a record ID in the query.
    record_id = extract_record_id(query)

    # Step 2: If a record ID is found, use the operational guidance flow.
    if record_id:
        guidance_response = generate_operational_guidance(
            record_id=record_id,
            top_k=top_k,
        )

        return {
            "query": query,
            "route": "operational_guidance",
            "record_id": record_id,
            "response": guidance_response,
        }

    # Step 3: If no record ID is found, use the normal RAG document flow.
    rag_response = generate_rag_answer(
        query=query,
        top_k=top_k,
    )

    return {
        "query": query,
        "route": "document_rag",
        "record_id": None,
        "response": rag_response,
    }