import re

from app.services.operational_guidance_service import generate_operational_guidance
from app.services.rag_answer_service import generate_rag_answer
from app.services.cosmos_memory_service import save_agent_state


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


def orchestrate_user_query(
    query: str,
    top_k: int = 8,
    conversation_id: str | None = None,
) -> dict:
    """
    Main orchestration service for the copilot.

    What this function does:
    1. Receives the user's natural language query.
    2. Checks whether the query contains a record ID.
    3. If record ID exists, routes to operational guidance.
    4. If no record ID exists, routes to document RAG.
    5. Saves agent state into Cosmos DB when conversation_id is provided.
    6. Returns a consistent response with route information.

    conversation_id is optional:
    - If provided, state is saved to Cosmos DB.
    - If not provided, the copilot still works without memory.
    """

    # Step 1: Try to find a record ID in the query.
    record_id = extract_record_id(query)

    # Step 2: If a record ID is found, use the operational guidance flow.
    if record_id:
        guidance_response = generate_operational_guidance(
            record_id=record_id,
            top_k=top_k,
        )

        # Pull memory fields from the operational guidance response.
        policy_guidance = guidance_response.get("policy_guidance") or {}

        response_summary = policy_guidance.get("answer")

        if response_summary and len(response_summary) > 500:
            response_summary = response_summary[:500] + "..."

        # Save state to Cosmos DB only when a conversation_id is provided.
        if conversation_id:
            save_agent_state(
                conversation_id=conversation_id,
                user_query=query,
                route="operational_guidance",
                response_summary=response_summary,
                record_id=record_id,
                business_domain=guidance_response.get("business_domain"),
                confidence_score=policy_guidance.get("confidence_score"),
                confidence_label=policy_guidance.get("confidence_label"),
                human_review_required=policy_guidance.get("human_review_required"),
            )

        return {
            "query": query,
            "conversation_id": conversation_id,
            "route": "operational_guidance",
            "record_id": record_id,
            "memory_saved": conversation_id is not None,
            "response": guidance_response,
        }

    # Step 3: If no record ID is found, use the normal RAG document flow.
    rag_response = generate_rag_answer(
        query=query,
        top_k=top_k,
    )

    response_summary = rag_response.get("answer")

    if response_summary and len(response_summary) > 500:
        response_summary = response_summary[:500] + "..."

    # Save document RAG state to Cosmos DB only when conversation_id is provided.
    if conversation_id:
        save_agent_state(
            conversation_id=conversation_id,
            user_query=query,
            route="document_rag",
            response_summary=response_summary,
            record_id=None,
            business_domain=rag_response.get("business_domain"),
            confidence_score=rag_response.get("confidence_score"),
            confidence_label=rag_response.get("confidence_label"),
            human_review_required=rag_response.get("human_review_required"),
        )

    return {
        "query": query,
        "conversation_id": conversation_id,
        "route": "document_rag",
        "record_id": None,
        "memory_saved": conversation_id is not None,
        "response": rag_response,
    }