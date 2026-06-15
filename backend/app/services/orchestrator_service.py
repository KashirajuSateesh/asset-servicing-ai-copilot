import re

from app.services.cosmos_memory_service import save_agent_state
from app.services.audit_log_service import save_audit_event
from app.services.mcp_client_service import (
    mcp_operational_guidance,
    mcp_policy_document_answer,
    mcp_latest_memory_state,
)


def extract_record_id(query: str) -> str | None:
    """
    Extracts an operational record ID from the user query.
    """

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
    """

    if response_summary and len(response_summary) > 500:
        return response_summary[:500] + "..."

    return response_summary


def extract_latest_state_from_mcp_response(memory_response: dict) -> dict | None:
    """
    Safely extracts latest memory state from MCP memory response.

    Different backend endpoints may return memory as:
    - direct state dict
    - {"state": {...}}
    - {"latest_state": {...}}
    - {"memory_state": {...}}

    This helper makes the orchestrator flexible.
    """

    if not memory_response:
        return None

    if memory_response.get("record_id"):
        return memory_response

    for key in ["state", "latest_state", "memory_state", "agent_state", "data"]:
        value = memory_response.get(key)

        if isinstance(value, dict):
            return value

    return None


def get_answer_from_response(response: dict) -> str | None:
    """
    Extracts answer text from either RAG response or operational guidance response.
    """

    if not response:
        return None

    if response.get("answer"):
        return response.get("answer")

    policy_guidance = response.get("policy_guidance")

    if isinstance(policy_guidance, dict):
        return policy_guidance.get("answer")

    return None


def get_policy_metrics(response: dict) -> dict:
    """
    Extracts confidence, label, and human review values from response.
    """

    if not response:
        return {}

    policy_guidance = response.get("policy_guidance")

    if isinstance(policy_guidance, dict):
        return {
            "confidence_score": policy_guidance.get("confidence_score"),
            "confidence_label": policy_guidance.get("confidence_label"),
            "human_review_required": policy_guidance.get("human_review_required"),
        }

    return {
        "confidence_score": response.get("confidence_score"),
        "confidence_label": response.get("confidence_label"),
        "human_review_required": response.get("human_review_required"),
    }


async def orchestrate_user_query(
    query: str,
    top_k: int = 8,
    conversation_id: str | None = None,
    request_id: str | None = None,
) -> dict:
    """
    Main orchestration service for the copilot.

    This version uses MCP tools instead of directly calling backend services.

    Flow:
    1. Detect record ID.
    2. If follow-up, recover latest memory using MCP.
    3. If record ID exists, call MCP operational_guidance tool.
    4. If no record ID, call MCP policy_document_answer tool.
    5. Save memory and audit logs from backend.
    """

    record_id = extract_record_id(query)
    memory_used = False

    # Step 1: Follow-up memory recovery through MCP.
    if not record_id and conversation_id and is_follow_up_query(query):
        memory_response = await mcp_latest_memory_state(conversation_id)
        latest_state = extract_latest_state_from_mcp_response(memory_response)

        if latest_state and latest_state.get("record_id"):
            record_id = latest_state.get("record_id")
            memory_used = True

    # Step 2: Operational guidance route through MCP.
    if record_id:
        guidance_response = await mcp_operational_guidance(
            record_id=record_id,
            top_k=top_k,
        )

        metrics = get_policy_metrics(guidance_response)

        response_summary = shorten_response_summary(
            get_answer_from_response(guidance_response)
        )

        if conversation_id:
            save_agent_state(
                conversation_id=conversation_id,
                user_query=query,
                route="operational_guidance",
                response_summary=response_summary,
                record_id=record_id,
                business_domain=guidance_response.get("business_domain"),
                confidence_score=metrics.get("confidence_score"),
                confidence_label=metrics.get("confidence_label"),
                human_review_required=metrics.get("human_review_required"),
            )

        save_audit_event(
            event_type="copilot_request",
            route="operational_guidance",
            conversation_id=conversation_id,
            user_query=query,
            record_id=record_id,
            business_domain=guidance_response.get("business_domain"),
            confidence_score=metrics.get("confidence_score"),
            confidence_label=metrics.get("confidence_label"),
            human_review_required=metrics.get("human_review_required"),
            memory_used=memory_used,
            memory_saved=conversation_id is not None,
            status="success",
            request_id=request_id,
        )

        return {
            "query": query,
            "conversation_id": conversation_id,
            "request_id": request_id,
            "execution_mode": "mcp",
            "mcp_tool_used": "operational_guidance",
            "route": "operational_guidance",
            "record_id": record_id,
            "memory_used": memory_used,
            "memory_saved": conversation_id is not None,
            "response": guidance_response,
        }

    # Step 3: Document RAG route through MCP.
    rag_response = await mcp_policy_document_answer(
        query=query,
        top_k=top_k,
    )

    metrics = get_policy_metrics(rag_response)

    response_summary = shorten_response_summary(
        get_answer_from_response(rag_response)
    )

    if conversation_id:
        save_agent_state(
            conversation_id=conversation_id,
            user_query=query,
            route="document_rag",
            response_summary=response_summary,
            record_id=None,
            business_domain=rag_response.get("business_domain"),
            confidence_score=metrics.get("confidence_score"),
            confidence_label=metrics.get("confidence_label"),
            human_review_required=metrics.get("human_review_required"),
        )

    save_audit_event(
        event_type="copilot_request",
        route="document_rag",
        conversation_id=conversation_id,
        user_query=query,
        record_id=None,
        business_domain=rag_response.get("business_domain"),
        confidence_score=metrics.get("confidence_score"),
        confidence_label=metrics.get("confidence_label"),
        human_review_required=metrics.get("human_review_required"),
        memory_used=memory_used,
        memory_saved=conversation_id is not None,
        status="success",
        request_id=request_id,
    )

    return {
        "query": query,
        "conversation_id": conversation_id,
        "request_id": request_id,
        "execution_mode": "mcp",
        "mcp_tool_used": "policy_document_answer",
        "route": "document_rag",
        "record_id": None,
        "memory_used": memory_used,
        "memory_saved": conversation_id is not None,
        "response": rag_response,
    }