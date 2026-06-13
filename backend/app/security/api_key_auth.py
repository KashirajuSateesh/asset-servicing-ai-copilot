from fastapi import Header, HTTPException, status

from app.config import settings


def verify_copilot_api_key(
    x_copilot_api_key: str | None = Header(default=None),
) -> bool:
    """
    Verifies the API key sent by the frontend or client.

    Why this is useful:
    We do not want protected copilot endpoints to be open without any access control.

    The client must send this header:
    x-copilot-api-key: <key>

    For local demo:
    COPILOT_API_KEY is stored in backend/.env

    In production:
    This can be replaced with Azure Entra ID / OAuth / RBAC.
    """

    # If the backend API key is missing, fail closed.
    # This avoids accidentally exposing protected endpoints.
    if not settings.copilot_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Copilot API key is not configured on the server.",
        )

    # If the client did not send the API key, reject the request.
    if not x_copilot_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing copilot API key.",
        )

    # If the client key does not match the server key, reject the request.
    if x_copilot_api_key != settings.copilot_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid copilot API key.",
        )

    return True