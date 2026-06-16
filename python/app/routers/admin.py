"""管理员路由。

包含后台统计、角色、菜单、权限以及角色权限/权限菜单绑定。
这些接口主要供管理端使用，均要求当前用户为 admin。
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.course import Course
from app.db.models.question import Question
from app.db.models.teaching_class import TeachingClass
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.schemas.api_response import api_success
from app.services.menu_service import MenuService
from app.services.permission_service import PermissionService
from app.services.role_service import RoleService

router = APIRouter(prefix="/admin", tags=["admin"])


class RoleIn(BaseModel):
    role_name: str = Field(min_length=1, max_length=20)


class AssignRoleIn(BaseModel):
    user_id: int
    role_name: str


class MenuIn(BaseModel):
    menu_name: str = Field(min_length=1, max_length=50)
    description: str | None = None


class PermissionIn(BaseModel):
    permission_name: str = Field(min_length=1, max_length=100)
    permission_code: str = Field(min_length=1, max_length=100)
    description: str | None = None


class RolePermissionIn(BaseModel):
    role_id: int
    permission_id: int


class PermissionMenuIn(BaseModel):
    permission_id: int
    menu_id: int


def _require_admin(user: User) -> None:
    """管理员权限校验。"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")


@router.get("/dashboard/stats")
async def get_admin_dashboard_stats(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """后台首页统计：用户角色分布、课程数、教学班数、题目数。"""
    _require_admin(current_user)
    role_rows = (await db.execute(select(User.role, func.count(User.user_id)).where(User.status != "deleted").group_by(User.role))).all()
    role_counts = {role: count for role, count in role_rows}
    course_count = await db.scalar(select(func.count(Course.course_id)).where(Course.is_deleted == 0))
    class_count = await db.scalar(select(func.count(TeachingClass.class_id)).where(TeachingClass.is_deleted == 0))
    question_count = await db.scalar(select(func.count(Question.question_id)))
    roles = [{"role": role, "count": int(role_counts.get(role, 0))} for role in ("admin", "teacher", "student")]
    return api_success({
        "total_users": int(sum(item["count"] for item in roles)),
        "roles": roles,
        "course_count": int(course_count or 0),
        "class_count": int(class_count or 0),
        "question_count": int(question_count or 0),
    }, message="Admin dashboard stats fetched successfully")


# =========================
# 角色管理
# =========================
@router.get("/roles")
async def list_roles(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    return api_success(await RoleService(db).list_roles(), message="Roles fetched successfully")


@router.post("/roles")
async def create_role(req: RoleIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    try:
        return api_success(await RoleService(db).create_role(req.role_name), message="Role created successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/roles/{role_id}")
async def update_role(role_id: int, req: RoleIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    try:
        return api_success(await RoleService(db).update_role(role_id, req.role_name), message="Role updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/roles/{role_id}")
async def delete_role(role_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    try:
        return api_success(await RoleService(db).delete_role(role_id), message="Role deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/user-roles")
async def assign_role_to_user(req: AssignRoleIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """给用户分配角色，适配 user_roles.user_id 唯一的设计。"""
    _require_admin(current_user)
    try:
        return api_success(await RoleService(db).assign_role_to_user(req.user_id, req.role_name), message="User role assigned successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# =========================
# 菜单管理
# =========================
@router.get("/menus")
async def list_menus(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    return api_success(await MenuService(db).list_menus(), message="Menus fetched successfully")


@router.post("/menus")
async def create_menu(req: MenuIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    return api_success(await MenuService(db).create_menu(req.menu_name, req.description), message="Menu created successfully")


@router.patch("/menus/{menu_id}")
async def update_menu(menu_id: int, req: MenuIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    try:
        return api_success(await MenuService(db).update_menu(menu_id, req.menu_name, req.description), message="Menu updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/menus/{menu_id}")
async def delete_menu(menu_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    try:
        return api_success(await MenuService(db).delete_menu(menu_id), message="Menu deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# =========================
# 权限管理
# =========================
@router.get("/permissions")
async def list_permissions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    return api_success(await PermissionService(db).list_permissions(), message="Permissions fetched successfully")


@router.post("/permissions")
async def create_permission(req: PermissionIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    try:
        return api_success(await PermissionService(db).create_permission(req.permission_name, req.permission_code, req.description), message="Permission created successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/permissions/{permission_id}")
async def update_permission(permission_id: int, req: PermissionIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    try:
        return api_success(await PermissionService(db).update_permission(permission_id, **req.model_dump(exclude_unset=True)), message="Permission updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/permissions/{permission_id}")
async def delete_permission(permission_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    try:
        return api_success(await PermissionService(db).delete_permission(permission_id), message="Permission deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/role-permissions")
async def assign_permission_to_role(req: RolePermissionIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """给角色绑定权限。"""
    _require_admin(current_user)
    try:
        return api_success(await PermissionService(db).assign_permission_to_role(req.role_id, req.permission_id), message="Permission assigned to role successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/roles/{role_id}/permissions")
async def get_role_permissions(role_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    return api_success(await PermissionService(db).get_role_permissions(role_id), message="Role permissions fetched successfully")


@router.delete("/roles/{role_id}/permissions/{permission_id}")
async def remove_permission_from_role(role_id: int, permission_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    return api_success(await PermissionService(db).remove_permission_from_role(role_id, permission_id), message="Role permission removed successfully")


@router.post("/permission-menus")
async def bind_permission_menu(req: PermissionMenuIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """给权限绑定菜单。"""
    _require_admin(current_user)
    try:
        return api_success(await PermissionService(db).bind_permission_menu(req.permission_id, req.menu_id), message="Permission menu bound successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/permissions/{permission_id}/menus/{menu_id}")
async def remove_permission_menu(permission_id: int, menu_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    return api_success(await PermissionService(db).remove_permission_menu(permission_id, menu_id), message="Permission menu removed successfully")
