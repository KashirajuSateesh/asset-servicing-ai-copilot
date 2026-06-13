from fastapi import APIRouter, HTTPException

from app.services.cosmos_memory_service import (
    get_latest_agent_state,
    list_agent_states,
    save_agent_state,
)


router = APIRouter(
    prefix="/memory",
    tags=["Agent Memory"],
)


@router.post("/state")
def create_memory_state(
    conversation_id: str,
    user_query: str,
    route: str,
    response_summary: str | None = None,
    record_id: str | None = None,
    business_domain: str | None = None,
    confidence_score: float | None = None,
    confidence_label: str | None = None,
    human_review_required: bool | None = None,
):
    """
    Saves one agent state event into Azure Cosmos DB.

    What this endpoint does:
    1. Takes conversation and routing details.
    2. Saves them as a JSON document in Cosmos DB.
    3. Returns the saved state document.

    This is only for testing memory writes.
    Later, the orchestrator will save this automatically.
    """

    try:
        return save_agent_state(
            conversation_id=conversation_id,
            user_query=user_query,
            route=route,
            response_summary=response_summary,
            record_id=record_id,
            business_domain=business_domain,
            confidence_score=confidence_score,
            confidence_label=confidence_label,
            human_review_required=human_review_required,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save memory state: {str(exc)}",
        )


@router.get("/state/latest/{conversation_id}")
def get_latest_memory_state(conversation_id: str):
    """
    Gets the latest saved state for a conversation.

    This helps test whether Cosmos DB can retrieve the most recent memory.
    """

    try:
        latest_state = get_latest_agent_state(conversation_id)

        if not latest_state:
            return {
                "conversation_id": conversation_id,
                "found": False,
                "state": None,
            }

        return {
            "conversation_id": conversation_id,
            "found": True,
            "state": latest_state,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get latest memory state: {str(exc)}",
        )


@router.get("/state/history/{conversation_id}")
def get_memory_state_history(conversation_id: str, limit: int = 10):
    """
    Lists recent memory states for a conversation.

    This helps us verify that multiple user turns are being stored.
    """

    try:
        if limit < 1 or limit > 50:
            raise HTTPException(
                status_code=400,
                detail="limit must be between 1 and 50.",
            )

        states = list_agent_states(
            conversation_id=conversation_id,
            limit=limit,
        )

        return {
            "conversation_id": conversation_id,
            "count": len(states),
            "states": states,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get memory history: {str(exc)}",
        )