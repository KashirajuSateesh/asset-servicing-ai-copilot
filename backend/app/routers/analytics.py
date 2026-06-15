from fastapi import APIRouter, Depends, HTTPException

from app.security.rbac import get_current_role, require_permission
from app.services.analytics_service import get_analytics_summary


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/summary")
def analytics_summary(role: str = Depends(get_current_role)):
    """
    Returns analytics data for Dashboard.

    RBAC:
    User must have analytics permission.
    """

    require_permission("analytics", role)

    try:
        return get_analytics_summary()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load analytics summary: {str(exc)}",
        )