from fastapi import APIRouter

from app.services.system_health_service import get_system_health


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