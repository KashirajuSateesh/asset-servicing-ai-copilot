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