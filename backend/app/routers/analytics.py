from fastapi import APIRouter, HTTPException

from app.services.analytics_service import get_analytics_summary


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/summary")
def analytics_summary():
    """
    Returns analytics data for the frontend Analytics page.

    This endpoint combines:
    - operational counts from Azure SQL
    - copilot usage metrics from Cosmos audit logs
    - retrieval/indexing summary
    """

    try:
        return get_analytics_summary()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load analytics summary: {str(exc)}",
        )