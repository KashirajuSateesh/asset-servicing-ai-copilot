from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, HTTPException, status

from app.services.auth_service import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.services.user_service import (
    create_pending_user,
    get_user_by_email,
    list_all_users,
    approve_user,
)


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class BootstrapAdminRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


@router.post("/signup")
def signup(request: SignupRequest):
    """
    Creates a signup request.

    New users are saved as:
    status = pending
    role = unassigned

    Admin must approve the user before login.
    """

    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters.",
        )

    try:
        hashed_password = hash_password(request.password)

        user = create_pending_user(
            name=request.name,
            email=request.email,
            hashed_password=hashed_password,
        )

        return {
            "message": "Signup request submitted. Waiting for admin approval.",
            "user": {
                "user_id": user["user_id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
                "status": user["status"],
            },
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.post("/login")
def login(request: LoginRequest):
    """
    Logs in an approved user.

    Pending users cannot login.
    """

    user = get_user_by_email(request.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    password_valid = verify_password(
        plain_password=request.password,
        hashed_password=user["hashed_password"],
    )

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if user.get("status") == "pending":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not approved yet. Please wait for admin approval.",
        )

    if user.get("status") == "disabled" or user.get("access_enabled") is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User access is disabled. Please contact admin.",
        )

    if user.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not active.",
        )

    token_user_data = {
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"],
        "role": user.get("role", "unassigned"),
        "roles": user.get("roles", [user.get("role")] if user.get("role") else []),
        "status": user["status"],
        "access_enabled": user.get("access_enabled", True),
    }

    access_token = create_access_token(token_user_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": token_user_data,
    }

@router.post("/bootstrap-admin")
def bootstrap_admin(request: BootstrapAdminRequest):
    """
    Creates or repairs the first admin user for local development.

    If no users exist:
    - create first admin

    If the requested email already exists but is still pending:
    - approve that user as admin

    This is only for local development bootstrap.
    """

    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters.",
        )

    existing_user = get_user_by_email(request.email)

    if existing_user:
        if existing_user.get("status") == "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bootstrap blocked. Admin user is already active.",
            )

        approved_user = approve_user(
            user_id=existing_user["user_id"],
            role="admin",
            approved_by="bootstrap-repair",
        )

        token_user_data = {
            "user_id": approved_user["user_id"],
            "name": approved_user["name"],
            "email": approved_user["email"],
            "role": approved_user["role"],
            "status": approved_user["status"],
        }

        access_token = create_access_token(token_user_data)

        return {
            "message": "Existing pending admin approved successfully.",
            "access_token": access_token,
            "token_type": "bearer",
            "user": token_user_data,
        }

    existing_users = list_all_users()

    if existing_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bootstrap blocked. Users already exist. Use admin approval flow.",
        )

    hashed_password = hash_password(request.password)

    user = create_pending_user(
        name=request.name,
        email=request.email,
        hashed_password=hashed_password,
    )

    approved_user = approve_user(
        user_id=user["user_id"],
        role="admin",
        approved_by="bootstrap",
    )

    token_user_data = {
        "user_id": approved_user["user_id"],
        "name": approved_user["name"],
        "email": approved_user["email"],
        "role": approved_user["role"],
        "status": approved_user["status"],
    }

    access_token = create_access_token(token_user_data)

    return {
        "message": "Bootstrap admin created successfully.",
        "access_token": access_token,
        "token_type": "bearer",
        "user": token_user_data,
    }