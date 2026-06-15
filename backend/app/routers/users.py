from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status

from app.security.token_auth import get_current_user
from app.security.rbac import require_permission
from app.services.user_service import (
    approve_user,
    list_all_users,
    list_pending_users,
    update_user_access,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


class ApproveUserRequest(BaseModel):
    role: str

class UpdateUserAccessRequest(BaseModel):
    roles: list[str]
    access_enabled: bool


def sanitize_user(user: dict) -> dict:
    """
    Removes sensitive fields before returning user data to frontend.
    """

    return {
        "user_id": user.get("user_id"),
        "name": user.get("name"),
        "email": user.get("email"),
        "role": user.get("role"),
        "roles": user.get("roles", [user.get("role")] if user.get("role") else []),
        "status": user.get("status"),
        "access_enabled": user.get("access_enabled", user.get("status") == "active"),
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at"),
        "approved_at": user.get("approved_at"),
        "approved_by": user.get("approved_by"),
    }


@router.get("/pending")
def get_pending_users(current_user: dict = Depends(get_current_user)):
    """
    Admin can view pending signup requests.
    """

    require_permission("users_admin", current_user["role"])

    users = list_pending_users()

    return {
        "users": [sanitize_user(user) for user in users],
        "count": len(users),
    }


@router.get("")
def get_all_users(current_user: dict = Depends(get_current_user)):
    """
    Admin can view all users.
    """

    require_permission("users_admin", current_user["role"])

    users = list_all_users()

    return {
        "users": [sanitize_user(user) for user in users],
        "count": len(users),
    }


@router.post("/{user_id}/approve")
def approve_pending_user(
    user_id: str,
    request: ApproveUserRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Admin approves a pending user and assigns a role.
    """

    require_permission("users_admin", current_user["role"])

    allowed_roles = {
        "admin",
        "operations_analyst",
        "reconciliation_analyst",
        "case_manager",
        "policy_reviewer",
        "read_only",
    }

    if request.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {request.role}",
        )

    approved_user = approve_user(
        user_id=user_id,
        role=request.role,
        approved_by=current_user["email"],
    )

    return {
        "message": "User approved successfully.",
        "user": sanitize_user(approved_user),
    }

@router.patch("/{user_id}/access")
def update_user_roles_and_access(
    user_id: str,
    request: UpdateUserAccessRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Admin can update user roles and enable/disable login access.
    """

    require_permission("users_admin", current_user["role"])

    allowed_roles = {
        "admin",
        "operations_analyst",
        "reconciliation_analyst",
        "case_manager",
        "policy_reviewer",
        "read_only",
    }

    invalid_roles = [role for role in request.roles if role not in allowed_roles]

    if invalid_roles:
      raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail=f"Invalid roles: {invalid_roles}",
      )

    updated_user = update_user_access(
        user_id=user_id,
        roles=request.roles,
        access_enabled=request.access_enabled,
        updated_by=current_user["email"],
    )

    return {
        "message": "User access updated successfully.",
        "user": sanitize_user(updated_user),
    }