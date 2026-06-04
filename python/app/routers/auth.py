from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.user_access import ensure_user_access
from app.schemas.api_response import api_success
from app.schemas.auth import LoginRequest
from app.schemas.user_response import user_to_dict
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    req: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    result = await auth_service.login(req.username, req.pwd)

    if not result:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    return api_success(result, message="Login successful")


@router.post("/register")
async def register(
    req: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)

    try:
        user = await auth_service.register_user(req.username, req.pwd)
        return api_success(
            {"user": user_to_dict(user)},
            message="Registration successful",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return api_success(
        user_to_dict(current_user),
        message="Current user fetched successfully",
    )


@router.post("/logout")
async def logout():
    return api_success(None, message="Logout successful")


@router.get("/info/{user_id}")
async def get_user_info(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ensure_user_access(current_user, user_id)
    auth_service = AuthService(db)

    try:
        user_info = await auth_service.get_user_info(user_id)
        return api_success(user_info, message="User info retrieved successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/delete/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ensure_user_access(current_user, user_id)
    auth_service = AuthService(db)

    try:
        result = await auth_service.delete_user(user_id)
        return api_success(result, message="User deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
