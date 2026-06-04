from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.user_access import ensure_user_access
from app.schemas.api_response import api_success
from app.schemas.auth import ChangePasswordRequest
from app.services.auth_service import AuthService
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/profile/{user_id}")
async def get_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ensure_user_access(current_user, user_id)
    service = ProfileService(db)
    try:
        profile = await service.get_profile(user_id)
        return api_success(profile, message="Profile fetched successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/change-password")
async def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    try:
        result = await auth_service.change_password(
            current_user.user_id,
            req.old_password,
            req.new_password,
        )
        return api_success(result, message="Password changed successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
