from fastapi import APIRouter, HTTPException

from app.services.audit_log_service import list_audit_events


router = APIRouter(
    prefix="/audit",
    tags=["Audit Logs"],
)


@router.get("/events/{conversation_id}")
def get_audit_events(conversation_id: str, limit: int = 20):
    """
    Lists audit events for a conversation.

    What this endpoint does:
    1. Accepts a conversation_id.
    2. Reads only audit_event documents from Cosmos DB.
    3. Returns route decisions, record IDs, confidence, memory usage,
       and human review flags.

    This supports observability and traceability for the copilot.
    """

    try:
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=400,
                detail="limit must be between 1 and 100.",
            )

        events = list_audit_events(
            conversation_id=conversation_id,
            limit=limit,
        )

        return {
            "conversation_id": conversation_id,
            "count": len(events),
            "events": events,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list audit events: {str(exc)}",
        )