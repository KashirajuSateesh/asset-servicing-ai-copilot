import re

from app.services.cosmos_memory_service import (
    get_latest_agent_state,
    save_agent_state,
)
from app.services.operational_guidance_service import generate_operational_guidance
from app.services.rag_answer_service import generate_rag_answer
from app.services.audit_log_service import save_audit_event


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


def is_follow_up_query(query: str) -> bool:
    """
    Detects whether the user query looks like a follow-up question.

    Why this is useful:
    If the user asks something like:
    - "What should I do next?"
    - "Explain more"
    - "Is it breached?"
    - "What is the next action?"

    the query may not include the record ID again.
    In that case, the orchestrator can use Cosmos DB memory to recover
    the previous record_id from the same conversation.
    """

    query_lower = query.lower().strip()

    follow_up_keywords = [
        "what should i do next",
        "next step",
        "next action",
        "what next",
        "explain more",
        "tell me more",
        "is it breached",
        "is this breached",
        "should i escalate",
        "what about this",
        "for this",
        "this",
    ]

    return any(keyword in query_lower for keyword in follow_up_keywords)


def shorten_response_summary(response_summary: str | None) -> str | None:
    """
    Shortens the answer before saving it into Cosmos DB.

    Why this is useful:
    We do not need to store the full LLM answer as state memory.
    A short summary is enough for follow-up context and audit trail.
    """

    if response_summary and len(response_summary) > 500:
        return response_summary[:500] + "..."

    return response_summary


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
    3. If no record ID exists and query is a follow-up, checks Cosmos DB memory.
    4. If record ID exists or is recovered from memory, routes to operational guidance.
    5. If no record ID exists, routes to document RAG.
    6. Saves agent state into Cosmos DB when conversation_id is provided.
    7. Returns a consistent response with route and memory information.

    conversation_id is optional:
    - If provided, state is saved to Cosmos DB.
    - If provided during follow-up, previous record_id can be reused.
    - If not provided, the copilot still works without memory.
    """

    # Step 1: Try to find a record ID directly in the current query.
    record_id = extract_record_id(query)

    # Step 2: Track whether memory was used to recover missing context.
    memory_used = False

    # Step 3: If no record ID is found, check whether this is a follow-up query.
    # If it is a follow-up and conversation_id is provided, recover the last
    # record_id from Cosmos DB persistent memory.
    if not record_id and conversation_id and is_follow_up_query(query):
        latest_state = get_latest_agent_state(conversation_id)

        if latest_state and latest_state.get("record_id"):
            record_id = latest_state.get("record_id")
            memory_used = True

    # Step 4: If a record ID is found directly or recovered from memory,
    # route to operational guidance.
    if record_id:
        guidance_response = generate_operational_guidance(
            record_id=record_id,
            top_k=top_k,
        )

        # Pull memory fields from the operational guidance response.
        policy_guidance = guidance_response.get("policy_guidance") or {}

        response_summary = shorten_response_summary(
            policy_guidance.get("answer")
        )

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

        # Save audit event for observability and traceability.
        save_audit_event(
            event_type="copilot_request",
            route="operational_guidance",
            conversation_id=conversation_id,
            user_query=query,
            record_id=record_id,
            business_domain=guidance_response.get("business_domain"),
            confidence_score=policy_guidance.get("confidence_score"),
            confidence_label=policy_guidance.get("confidence_label"),
            human_review_required=policy_guidance.get("human_review_required"),
            memory_used=memory_used,
            memory_saved=conversation_id is not None,
            status="success",
        )

        return {
            "query": query,
            "conversation_id": conversation_id,
            "route": "operational_guidance",
            "record_id": record_id,
            "memory_used": memory_used,
            "memory_saved": conversation_id is not None,
            "response": guidance_response,
        }

    # Step 5: If no record ID is found and no memory was used, use normal
    # document RAG flow.
    rag_response = generate_rag_answer(
        query=query,
        top_k=top_k,
    )

    response_summary = shorten_response_summary(
        rag_response.get("answer")
    )

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

     # Save audit event for observability and traceability.
    save_audit_event(
        event_type="copilot_request",
        route="document_rag",
        conversation_id=conversation_id,
        user_query=query,
        record_id=None,
        business_domain=rag_response.get("business_domain"),
        confidence_score=rag_response.get("confidence_score"),
        confidence_label=rag_response.get("confidence_label"),
        human_review_required=rag_response.get("human_review_required"),
        memory_used=memory_used,
        memory_saved=conversation_id is not None,
        status="success",
    )

    return {
        "query": query,
        "conversation_id": conversation_id,
        "route": "document_rag",
        "record_id": None,
        "memory_used": memory_used,
        "memory_saved": conversation_id is not None,
        "response": rag_response,
    }