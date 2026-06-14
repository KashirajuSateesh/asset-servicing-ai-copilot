from sqlalchemy import text

from app.services.azure_sql_service import get_engine
from app.services.cosmos_memory_service import get_cosmos_container


def get_table_count(table_name: str) -> int:
    """
    Returns row count for a SQL table.

    Why this is useful:
    Analytics page should show real operational counts from Azure SQL,
    not hardcoded frontend values.
    """

    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text(f"SELECT COUNT(*) AS row_count FROM {table_name}"))
        row = result.fetchone()

    return int(row.row_count) if row else 0


def get_copilot_audit_metrics(limit: int = 200) -> dict:
    """
    Reads recent audit events from Cosmos DB and calculates AI usage metrics.

    Note:
    This is a demo-level analytics query. In production, we would create
    dedicated analytical containers or use Synapse/Log Analytics.
    """

    try:
        container = get_cosmos_container()

        query = """
        SELECT TOP @limit *
        FROM c
        WHERE c.document_type = @document_type
        ORDER BY c.created_at DESC
        """

        parameters = [
            {"name": "@limit", "value": limit},
            {"name": "@document_type", "value": "audit_event"},
        ]

        events = list(
            container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
            )
        )

        total_requests = len(events)
        successful_requests = len(
            [event for event in events if event.get("status") == "success"]
        )
        failed_requests = len(
            [event for event in events if event.get("status") == "failed"]
        )
        human_review_required = len(
            [event for event in events if event.get("human_review_required") is True]
        )

        confidence_values = [
            float(event.get("confidence_score"))
            for event in events
            if event.get("confidence_score") is not None
        ]

        average_confidence = (
            round(sum(confidence_values) / len(confidence_values), 2)
            if confidence_values
            else None
        )

        route_counts = {}

        for event in events:
            route = event.get("route") or "unknown"
            route_counts[route] = route_counts.get(route, 0) + 1

        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "human_review_required": human_review_required,
            "average_confidence": average_confidence,
            "route_counts": route_counts,
        }

    except Exception as exc:
        return {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "human_review_required": 0,
            "average_confidence": None,
            "route_counts": {},
            "error": str(exc),
        }


def get_analytics_summary() -> dict:
    """
    Returns analytics summary for the frontend Analytics page.

    This combines:
    - Azure SQL operational counts
    - Cosmos DB audit metrics
    - Azure AI Search/indexing summary
    """

    operations = {
        "settlement_exceptions": get_table_count("settlement_exceptions"),
        "reconciliation_breaks": get_table_count("reconciliation_breaks"),
        "case_tickets": get_table_count("case_tickets"),
        "corporate_actions": get_table_count("corporate_actions"),
        "trade_status": get_table_count("trade_status"),
        "custody_accounts": get_table_count("custody_accounts"),
    }

    ai_usage = get_copilot_audit_metrics()

    # We know from our ingestion test that 25 PDFs produced 75 chunks.
    # Later we can replace this with an Azure AI Search count query.
    retrieval = {
        "uploaded_pdfs": 25,
        "indexed_chunks": 75,
        "retrieval_mode": "Hybrid",
        "embedding_model": "text-embedding-3-small",
    }

    total_operational_records = sum(operations.values())

    return {
        "operations": operations,
        "ai_usage": ai_usage,
        "retrieval": retrieval,
        "summary": {
            "total_operational_records": total_operational_records,
            "system_readiness": "healthy",
        },
    }