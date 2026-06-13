from datetime import datetime, timezone
from uuid import uuid4

from app.services.cosmos_memory_service import get_cosmos_container


def utc_now_iso() -> str:
    """
    Returns current UTC time as an ISO string.

    We use UTC timestamps for consistent audit tracking.
    """

    return datetime.now(timezone.utc).isoformat()


def save_audit_event(
    event_type: str,
    route: str | None = None,
    conversation_id: str | None = None,
    user_query: str | None = None,
    record_id: str | None = None,
    business_domain: str | None = None,
    confidence_score: float | None = None,
    confidence_label: str | None = None,
    human_review_required: bool | None = None,
    memory_used: bool | None = None,
    memory_saved: bool | None = None,
    status: str = "success",
    error_message: str | None = None,
) -> dict:
    """
    Saves an audit event into Cosmos DB.

    Why this is useful:
    In enterprise GenAI systems, we need traceability:
    - What did the user ask?
    - Which route did the orchestrator choose?
    - Was memory used?
    - Was human review required?
    - Did the request fail?

    We store this as a separate document type inside the same Cosmos container.
    """

    container = get_cosmos_container()

    # If conversation_id is missing, use a system partition value.
    # This is required because the Cosmos partition key is /conversation_id.
    partition_conversation_id = conversation_id or "system_audit"

    audit_document = {
        "id": f"audit_{uuid4()}",
        "document_type": "audit_event",
        "event_type": event_type,
        "conversation_id": partition_conversation_id,
        "user_query": user_query,
        "route": route,
        "record_id": record_id,
        "business_domain": business_domain,
        "confidence_score": confidence_score,
        "confidence_label": confidence_label,
        "human_review_required": human_review_required,
        "memory_used": memory_used,
        "memory_saved": memory_saved,
        "status": status,
        "error_message": error_message,
        "created_at": utc_now_iso(),
    }

    container.create_item(body=audit_document)

    return audit_document