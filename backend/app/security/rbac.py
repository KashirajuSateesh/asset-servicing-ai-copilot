from fastapi import Header, HTTPException, status


# Demo RBAC roles used by the frontend and backend.
# In production, these roles would come from Azure Entra ID / OAuth claims.
VALID_ROLES = {
    "admin",
    "operations_analyst",
    "reconciliation_analyst",
    "case_manager",
    "policy_reviewer",
    "read_only",
}


ROLE_PERMISSIONS = {
    "admin": {
        "dashboard",
        "copilot",
        "documents",
        "exceptions",
        "reconciliation",
        "cases",
        "audit",
        "system",
        "analytics",
        "users_admin",
    },
    "operations_analyst": {
        "dashboard",
        "copilot",
        "exceptions",
        "documents",
        "analytics",
    },
    "reconciliation_analyst": {
        "dashboard",
        "copilot",
        "reconciliation",
        "documents",
        "analytics",
    },
    "case_manager": {
        "dashboard",
        "copilot",
        "cases",
        "documents",
        "analytics",
    },
    "policy_reviewer": {
        "dashboard",
        "copilot",
        "documents",
        "analytics",
    },
    "read_only": {
        "dashboard",
        "documents",
        "analytics",
    },
}


def get_current_role(x_user_role: str | None = Header(default="read_only")) -> str:
    """
    Reads the user role from request header.

    Header used by frontend:
    x-user-role: admin

    This is demo RBAC.
    In production, this would be replaced with JWT token validation.
    """

    role = (x_user_role or "read_only").strip().lower()

    if role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid role: {role}",
        )

    return role


def require_permission(permission: str, role: str) -> None:
    """
    Checks whether a role has a specific permission.
    Raises 403 if not allowed.
    """

    allowed_permissions = ROLE_PERMISSIONS.get(role, set())

    if permission not in allowed_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Role '{role}' does not have permission '{permission}'.",
        )