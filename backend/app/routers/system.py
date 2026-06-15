from fastapi import APIRouter

from app.services.system_health_service import get_system_health
from app.services.mcp_client_service import mcp_operational_guidance


router = APIRouter(
    prefix="/system",
    tags=["System Health"],
)


@router.get("/health")
def system_health():
    """
    Returns health status for the main copilot system components.

    This is useful for demos and operational checks:
    - backend
    - Azure SQL
    - Azure AI Search
    - Cosmos DB memory/audit
    - API key security
    - audit logging
    """

    return get_system_health()

@router.get("/mcp-test/{record_id}")
async def test_mcp_connection(record_id: str):
    """
    Tests if FastAPI can automatically start the MCP server
    and call an MCP tool.
    """

    result = await mcp_operational_guidance(
        record_id=record_id,
        top_k=5,
    )

    return {
        "mcp_status": "success",
        "record_id": record_id,
        "result": result,
    }