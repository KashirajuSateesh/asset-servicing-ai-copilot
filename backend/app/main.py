from fastapi import FastAPI
import uuid
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import copilot
from app.routers import documents
from app.routers import memory
from app.routers import operations
from app.services.azure_sql_service import test_sql_connection
from app.routers import audit
from app.routers import system
from app.routers import analytics



app = FastAPI(title=settings.app_name)

@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """
    Adds a unique request ID to every backend request.

    Why this is useful:
    If a request fails, we can trace the same request across
    frontend logs, backend logs, and audit records.

    The request ID is returned in the response header:
    x-request-id
    """

    # Use incoming request ID if the client already sends one.
    # Otherwise create a new UUID.
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())

    # Store the request ID in request.state so routers/services can use it later.
    request.state.request_id = request_id

    # Continue processing the request.
    response = await call_next(request)

    # Return request ID back to the client.
    response.headers["x-request-id"] = request_id

    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(operations.router)
app.include_router(copilot.router)
app.include_router(memory.router)
app.include_router(audit.router)
app.include_router(system.router)
app.include_router(analytics.router)

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

@app.get("/sql-check")
def sql_check():
    return test_sql_connection()