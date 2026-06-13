from fastapi import APIRouter, HTTPException

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
    6. Returns the routed response.

    This is the first memory-enabled Orchestrator Agent endpoint.
    """

    try:
        # Keep top_k controlled so we do not send too much context to the LLM.
        if top_k < 1 or top_k > 10:
            raise HTTPException(
                status_code=400,
                detail="top_k must be between 1 and 10.",
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
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process copilot query: {str(exc)}",
        )