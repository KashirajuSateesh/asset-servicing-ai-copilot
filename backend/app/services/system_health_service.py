from app.config import settings
from app.services.azure_sql_service import get_engine
from app.services.azure_search_service import get_search_client
from app.services.cosmos_memory_service import get_cosmos_container


def check_backend_status() -> dict:
    """
    Checks whether the FastAPI backend is running.
    If this function is executing, backend is already healthy.
    """

    return {
        "status": "healthy",
        "message": "Backend service is running.",
    }


def check_sql_status() -> dict:
    """
    Checks Azure SQL connectivity by opening a lightweight connection.

    Why this is useful:
    SQL is used for live operational records like trades, exceptions,
    reconciliation breaks, cases, and corporate actions.
    """

    try:
        engine = get_engine()

        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")

        return {
            "status": "healthy",
            "message": "Azure SQL connection successful.",
        }

    except Exception as exc:
        return {
            "status": "unhealthy",
            "message": str(exc),
        }


def check_search_status() -> dict:
    """
    Checks Azure AI Search connectivity.

    Why this is useful:
    Azure AI Search is used for hybrid retrieval over policy PDF chunks.
    """

    try:
        search_client = get_search_client()

        # Lightweight search call.
        results = search_client.search(
            search_text="settlement",
            top=1,
        )

        # Force the SDK to execute the request.
        list(results)

        return {
            "status": "healthy",
            "message": "Azure AI Search connection successful.",
        }

    except Exception as exc:
        return {
            "status": "unhealthy",
            "message": str(exc),
        }


def check_cosmos_status() -> dict:
    """
    Checks Azure Cosmos DB connectivity.

    Why this is useful:
    Cosmos DB stores agent memory, audit logs, and trace records.
    """

    try:
        container = get_cosmos_container()

        # Read container properties as a lightweight connectivity check.
        container.read()

        return {
            "status": "healthy",
            "message": "Azure Cosmos DB connection successful.",
        }

    except Exception as exc:
        return {
            "status": "unhealthy",
            "message": str(exc),
        }


def check_security_status() -> dict:
    """
    Checks whether API key security is configured.

    Why this is useful:
    The protected copilot endpoint requires x-copilot-api-key.
    """

    if settings.copilot_api_key:
        return {
            "status": "active",
            "message": "API key protection is configured.",
        }

    return {
        "status": "inactive",
        "message": "COPILOT_API_KEY is not configured.",
    }


def check_audit_status() -> dict:
    """
    Checks whether audit storage is reachable.

    For this project, audit logs are stored in the same Cosmos container.
    """

    cosmos_status = check_cosmos_status()

    if cosmos_status["status"] == "healthy":
        return {
            "status": "active",
            "message": "Audit logging storage is reachable.",
        }

    return {
        "status": "unhealthy",
        "message": "Audit logging storage is not reachable.",
    }


def get_system_health() -> dict:
    """
    Returns a single system health summary for demo and operations.

    This endpoint helps explain production readiness:
    - backend availability
    - SQL availability
    - search availability
    - Cosmos memory/audit availability
    - security configuration
    """

    backend = check_backend_status()
    sql = check_sql_status()
    search = check_search_status()
    cosmos = check_cosmos_status()
    security = check_security_status()

    # Audit logs are stored in the same Cosmos DB container.
    # So if Cosmos is healthy, audit logging storage is reachable.
    if cosmos["status"] == "healthy":
        audit = {
            "status": "active",
            "message": "Audit logging storage is reachable.",
        }
    else:
        audit = {
            "status": "unhealthy",
            "message": "Audit logging storage is not reachable.",
        }

    component_statuses = [
        backend["status"],
        sql["status"],
        search["status"],
        cosmos["status"],
        security["status"],
        audit["status"],
    ]

    has_unhealthy = any(status == "unhealthy" for status in component_statuses)
    has_inactive = any(status == "inactive" for status in component_statuses)

    if has_unhealthy:
        overall_status = "degraded"
    elif has_inactive:
        overall_status = "warning"
    else:
        overall_status = "healthy"

    return {
        "overall_status": overall_status,
        "components": {
            "backend": backend,
            "azure_sql": sql,
            "azure_ai_search": search,
            "cosmos_memory_audit": cosmos,
            "api_key_security": security,
            "audit_logging": audit,
        },
    }