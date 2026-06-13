from fastapi import APIRouter, Depends, HTTPException

from app.security.api_key_auth import verify_copilot_api_key
from app.services.audit_log_service import save_audit_event
from app.services.orchestrator_service import orchestrate_user_query


router = APIRouter(
    prefix="/copilot",
    tags=["Copilot Orchestrator"],
)


@router.get("/ask")
def ask_copilot(
    query: str,
    top_k: int = 8,
    conversation_id: str | None = None,
    authorized: bool = Depends(verify_copilot_api_key),
):
    """
    Main copilot endpoint.

    What this endpoint does:
    1. Accepts a natural language user question.
    2. Optionally accepts a conversation_id for persistent memory.
    3. Sends the query to the orchestrator service.
    4. The orchestrator decides which backend flow to use:
       - operational guidance if a record ID is found
       - document RAG if no record ID is found
    5. Saves agent state to Cosmos DB when conversation_id is provided.
    6. Saves audit events for both successful and failed requests.
    7. Returns the routed response.
    """

    try:
        # Keep top_k controlled so we do not send too much context to the LLM.
        if top_k < 1 or top_k > 10:
            error_message = "top_k must be between 1 and 10."

            # Save failed audit event before returning the validation error.
            save_audit_event(
                event_type="copilot_request",
                conversation_id=conversation_id,
                user_query=query,
                route="validation_error",
                record_id=None,
                business_domain=None,
                confidence_score=None,
                confidence_label=None,
                human_review_required=True,
                memory_used=False,
                memory_saved=False,
                status="failed",
                error_message=error_message,
            )

            raise HTTPException(
                status_code=400,
                detail=error_message,
            )

        # Route the user query to the correct backend flow.
        # If conversation_id is provided, the orchestrator will save state.
        response = orchestrate_user_query(
            query=query,
            top_k=top_k,
            conversation_id=conversation_id,
        )

        return response

    except HTTPException:
        # HTTPException is already handled above for known validation cases.
        # We re-raise it so FastAPI returns the correct status code.
        raise

    except Exception as exc:
        error_message = f"Failed to process copilot query: {str(exc)}"

        # Save failed audit event for unexpected backend errors.
        # This helps us debug SQL, RAG, OpenAI, Cosmos, or orchestration failures.
        save_audit_event(
            event_type="copilot_request",
            conversation_id=conversation_id,
            user_query=query,
            route="system_error",
            record_id=None,
            business_domain=None,
            confidence_score=None,
            confidence_label=None,
            human_review_required=True,
            memory_used=False,
            memory_saved=False,
            status="failed",
            error_message=error_message,
        )

        raise HTTPException(
            status_code=500,
            detail=error_message,
        )