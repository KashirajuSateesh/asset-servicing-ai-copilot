from app.backend_client import call_backend_get


async def get_operational_guidance(record_id: str, top_k: int = 8) -> dict:
    """
    MCP tool function for getting operational guidance.

    What this tool does:
    1. Accepts an operational record ID.
    2. Calls the FastAPI backend guidance endpoint.
    3. Returns SQL context + RAG policy guidance.

    Supported record examples:
    - TRD-0000001
    - EXC-000001
    - BRK-0000001
    - CASE-0000001
    """

    return await call_backend_get(
        path=f"/operations/guidance/{record_id}",
        params={
            "top_k": top_k,
        },
    )


async def ask_policy_documents(
    query: str,
    top_k: int = 8,
    business_domain: str | None = None,
) -> dict:
    """
    MCP tool function for asking policy/SOP document questions.

    What this tool does:
    1. Accepts a natural language policy question.
    2. Calls the FastAPI backend RAG endpoint.
    3. Returns the generated answer with citations and confidence score.

    Example questions:
    - When should settlement exceptions be escalated?
    - What evidence is needed for reconciliation breaks?
    - How should corporate action elections be processed?
    """

    params = {
        "query": query,
        "top_k": top_k,
    }

    # business_domain is optional.
    # If provided, backend retrieval will filter to that domain.
    if business_domain:
        params["business_domain"] = business_domain

    return await call_backend_get(
        path="/documents/ask",
        params=params,
    )


async def get_latest_memory_state(conversation_id: str) -> dict:
    """
    MCP tool function for retrieving latest conversation memory.

    What this tool does:
    1. Accepts a conversation ID.
    2. Calls the FastAPI backend memory endpoint.
    3. Returns the latest saved agent state from Cosmos DB.

    This helps the agent continue follow-up questions using persistent memory.
    """

    return await call_backend_get(
        path=f"/memory/state/latest/{conversation_id}",
    )