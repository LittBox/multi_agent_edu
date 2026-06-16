"""用户个人中心路由。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.user_access import ensure_user_access
from app.schemas.api_response import api_success
from app.services.auth_service import AuthService
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/user", tags=["user"])


class ProfileUpdateIn(BaseModel):
    """个人资料更新请求。"""
    username: str | None = None
    email: str | None = None
    avatar: str | None = None


class ChangePasswordIn(BaseModel):
    """修改密码请求。"""
    old_password: str
    new_password: str


@router.get("/profile/{user_id}")
async def get_profile(user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取个人档案和学习统计。"""
    ensure_user_access(current_user, user_id)
    try:
        data = await ProfileService(db).get_profile(user_id)
        return api_success(data, message="Profile fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/profile/{user_id}")
async def update_profile(user_id: int, req: ProfileUpdateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """更新个人资料。"""
    ensure_user_access(current_user, user_id)
    try:
        data = await ProfileService(db).update_profile(user_id, **req.model_dump(exclude_unset=True))
        return api_success(data, message="Profile updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/change-password")
async def change_password(req: ChangePasswordIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """修改当前登录用户密码。"""
    try:
        ok = await AuthService(db).change_password(current_user.user_id, req.old_password, req.new_password)
        return api_success(ok, message="Password changed successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
