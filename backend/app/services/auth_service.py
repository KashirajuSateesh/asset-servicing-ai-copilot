from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings


# bcrypt is used to safely hash passwords.
# We never store plain text passwords.
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Converts a plain password into a secure hashed password.
    """

    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks whether the login password matches the stored hashed password.
    """

    return password_context.verify(plain_password, hashed_password)


def create_access_token(user_data: dict[str, Any]) -> str:
    """
    Creates a JWT token after successful login.

    The token will contain:
    - user_id
    - email
    - name
    - role
    - status
    - expiry time
    """

    expire_time = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )

    token_payload = {
        **user_data,
        "exp": expire_time,
    }

    return jwt.encode(
        token_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decodes and validates JWT token.

    Returns None if token is invalid or expired.
    """

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        return payload

    except JWTError:
        return None