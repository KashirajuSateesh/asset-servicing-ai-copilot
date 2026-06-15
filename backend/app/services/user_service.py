from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.services.cosmos_memory_service import get_cosmos_container


def get_current_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_email(email: str) -> str:
    return email.strip().lower()


def create_pending_user(name: str, email: str, hashed_password: str) -> dict[str, Any]:
    """
    Creates a new signup request.

    New users are not active immediately.
    Admin must approve and assign a role.
    """

    container = get_cosmos_container()

    normalized_email = normalize_email(email)

    existing_user = get_user_by_email(normalized_email)

    if existing_user:
        raise ValueError("User already exists with this email.")

    user_id = str(uuid4())

    user_doc = {
        "id": user_id,
        "document_type": "user",
        "user_id": user_id,
        "name": name.strip(),
        "email": normalized_email,
        "hashed_password": hashed_password,
        "role": "unassigned",
        "roles": [],
        "status": "pending",
        "access_enabled": False,
        "created_at": get_current_timestamp(),
        "updated_at": get_current_timestamp(),
        "approved_at": None,
        "approved_by": None,
    }

    container.create_item(user_doc)

    return user_doc


def get_user_by_email(email: str) -> dict[str, Any] | None:
    """
    Finds a user by email from Cosmos DB.
    """

    container = get_cosmos_container()
    normalized_email = normalize_email(email)

    query = """
    SELECT TOP 1 *
    FROM c
    WHERE c.document_type = @document_type
    AND c.email = @email
    """

    parameters = [
        {"name": "@document_type", "value": "user"},
        {"name": "@email", "value": normalized_email},
    ]

    users = list(
        container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        )
    )

    return users[0] if users else None


def list_pending_users() -> list[dict[str, Any]]:
    """
    Admin can view users waiting for approval.
    """

    container = get_cosmos_container()

    query = """
    SELECT *
    FROM c
    WHERE c.document_type = @document_type
    AND c.status = @status
    ORDER BY c.created_at DESC
    """

    parameters = [
        {"name": "@document_type", "value": "user"},
        {"name": "@status", "value": "pending"},
    ]

    return list(
        container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        )
    )


def approve_user(user_id: str, role: str, approved_by: str) -> dict[str, Any]:
    """
    Admin approves a user and assigns the first role.

    Supports both:
    - role: old single-role field
    - roles: new multi-role field
    """

    container = get_cosmos_container()

    query = """
    SELECT TOP 1 *
    FROM c
    WHERE c.document_type = @document_type
    AND c.user_id = @user_id
    """

    parameters = [
        {"name": "@document_type", "value": "user"},
        {"name": "@user_id", "value": user_id},
    ]

    users = list(
        container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        )
    )

    if not users:
        raise ValueError(f"User not found: {user_id}")

    user_doc = users[0]

    user_doc["role"] = role
    user_doc["roles"] = [role]
    user_doc["status"] = "active"
    user_doc["access_enabled"] = True
    user_doc["approved_at"] = get_current_timestamp()
    user_doc["approved_by"] = approved_by
    user_doc["updated_at"] = get_current_timestamp()

    container.upsert_item(user_doc)

    return user_doc


def update_user_access(
    user_id: str,
    roles: list[str],
    access_enabled: bool,
    updated_by: str,
) -> dict[str, Any]:
    """
    Admin updates user roles and access.

    This supports:
    - changing role
    - assigning multiple roles
    - disabling login access
    - enabling login access again
    """

    container = get_cosmos_container()

    query = """
    SELECT TOP 1 *
    FROM c
    WHERE c.document_type = @document_type
    AND c.user_id = @user_id
    """

    parameters = [
        {"name": "@document_type", "value": "user"},
        {"name": "@user_id", "value": user_id},
    ]

    users = list(
        container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        )
    )

    if not users:
        raise ValueError(f"User not found: {user_id}")

    user_doc = users[0]

    cleaned_roles = sorted(set(role.strip().lower() for role in roles if role.strip()))

    user_doc["roles"] = cleaned_roles
    user_doc["role"] = cleaned_roles[0] if cleaned_roles else "unassigned"
    user_doc["access_enabled"] = access_enabled
    user_doc["status"] = "active" if access_enabled else "disabled"
    user_doc["updated_at"] = get_current_timestamp()
    user_doc["updated_by"] = updated_by

    container.upsert_item(user_doc)

    return user_doc


def list_all_users() -> list[dict[str, Any]]:
    """
    Admin can view all users.
    """

    container = get_cosmos_container()

    query = """
    SELECT *
    FROM c
    WHERE c.document_type = @document_type
    ORDER BY c.created_at DESC
    """

    parameters = [
        {"name": "@document_type", "value": "user"},
    ]

    return list(
        container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        )
    )