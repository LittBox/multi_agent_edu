"""认证路由。

负责登录、注册、当前用户信息、注销和用户状态管理。
注意：users.pwd 为密文存储，所有响应都不返回 pwd 字段。
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.user_access import ensure_user_access
from app.schemas.api_response import api_success
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginIn(BaseModel):
    """登录请求体。前端字段是 username/pwd/role。"""
    username: str = Field(min_length=1, max_length=50)
    pwd: str = Field(min_length=1)
    role: str | None = None


class RegisterIn(BaseModel):
    """注册请求体。密码会在 service/DAO 层加密。"""
    username: str = Field(min_length=1, max_length=50)
    pwd: str = Field(min_length=1)
    role: str = "student"
    email: str | None = None
    avatar: str | None = None


class UserProfileUpdateIn(BaseModel):
    """更新用户基础资料，不包含密码。"""
    username: str | None = None
    email: str | None = None
    avatar: str | None = None


class ChangePasswordIn(BaseModel):
    """修改密码请求体。"""
    old_password: str = Field(min_length=1)
    new_password: str = Field(min_length=1)


class UserStatusIn(BaseModel):
    """管理员更新用户状态。"""
    status: str


@router.post("/login")
async def login(req: LoginIn, db: AsyncSession = Depends(get_db)):
    """用户登录。role 不为空时会校验角色是否匹配。"""
    try:
        result = await AuthService(db).login(req.username, req.pwd, req.role)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    if not result:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return api_success(result, message="Login successful")


@router.post("/register")
async def register(req: RegisterIn, db: AsyncSession = Depends(get_db)):
    """注册用户。生产环境可按需要限制开放角色。"""
    try:
        user = await AuthService(db).register_user(req.username, req.pwd, role=req.role, email=req.email, avatar=req.avatar)
        return api_success(user, message="Registration successful")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取当前登录用户信息。"""
    data = await AuthService(db).get_user_info(current_user.user_id)
    return api_success(data, message="Current user fetched successfully")


@router.post("/logout")
async def logout():
    """JWT 无状态注销，前端清理 token 即可。"""
    return api_success(None, message="Logout successful")


@router.get("/info/{user_id}")
async def get_user_info(user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """查看指定用户信息。本人或管理员可访问。"""
    ensure_user_access(current_user, user_id)
    try:
        data = await AuthService(db).get_user_info(user_id)
        return api_success(data, message="User info retrieved successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/info/{user_id}")
async def update_user_profile(user_id: int, req: UserProfileUpdateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """更新用户基础资料，不修改密码。"""
    ensure_user_access(current_user, user_id)
    try:
        data = await AuthService(db).update_profile(user_id, **req.model_dump(exclude_unset=True))
        return api_success(data, message="User profile updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/change-password")
async def change_password(req: ChangePasswordIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """修改当前用户密码。"""
    try:
        ok = await AuthService(db).change_password(current_user.user_id, req.old_password, req.new_password)
        return api_success(ok, message="Password changed successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/status/{user_id}")
async def update_user_status(user_id: int, req: UserStatusIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """管理员启用、停用或删除用户。"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    try:
        ok = await AuthService(db).update_status(user_id, req.status)
        return api_success(ok, message="User status updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
