import os

import httpx
from dotenv import load_dotenv


# Load environment variables from mcp_server/.env
load_dotenv()


BACKEND_API_BASE_URL = os.getenv(
    "BACKEND_API_BASE_URL",
    "http://127.0.0.1:8000",
)


def get_backend_url(path: str) -> str:
    """
    Builds a full backend API URL.

    Example:
    path = "/operations/guidance/EXC-000001"

    returns:
    http://127.0.0.1:8000/operations/guidance/EXC-000001
    """

    return f"{BACKEND_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"


async def call_backend_get(path: str, params: dict | None = None) -> dict:
    """
    Calls a GET endpoint from the FastAPI backend.

    Why this is useful:
    MCP tools should not duplicate database/RAG logic.
    They should call backend APIs that already work.
    """

    url = get_backend_url(path)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(
            url,
            params=params,
        )

        response.raise_for_status()

        return response.json()