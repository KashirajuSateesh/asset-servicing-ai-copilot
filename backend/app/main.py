from fastapi import FastAPI

from app.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Backend API for Asset Servicing AI Copilot project",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} is running",
        "environment": settings.app_env,
        "status": "ok",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "backend",
        "environment": settings.app_env,
    }


@app.get("/config-check")
def config_check():
    return {
        "openai_configured": bool(settings.openai_api_key),
        "azure_sql_configured": all(
            [
                settings.azure_sql_server,
                settings.azure_sql_database,
                settings.azure_sql_username,
                settings.azure_sql_password,
            ]
        ),
        "azure_blob_configured": all(
            [
                settings.azure_storage_account_name,
                settings.azure_storage_connection_string,
            ]
        ),
        "azure_search_configured": all(
            [
                settings.azure_search_endpoint,
                settings.azure_search_key,
                settings.azure_search_index_name,
            ]
        ),
    }