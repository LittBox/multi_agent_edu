"""权限、角色权限、权限菜单服务。"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.menuDao import MenuDAO
from app.dao.permissionDao import PermissionDAO, PermissionMenuDAO, RolePermissionDAO
from app.dao.roleDao import RoleDAO


class PermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def permission_to_dict(p) -> dict:
        return {"permission_id": p.permission_id, "permission_name": p.permission_name, "permission_code": p.permission_code, "description": p.description}

    async def create_permission(self, permission_name: str, permission_code: str, description: str | None = None) -> dict:
        if await PermissionDAO.get_by_code(self.db, permission_code):
            raise ValueError("Permission code already exists")
        p = await PermissionDAO.create_permission(self.db, permission_name, permission_code, description)
        return self.permission_to_dict(p)

    async def list_permissions(self) -> list[dict]:
        return [self.permission_to_dict(p) for p in await PermissionDAO.get_all(self.db)]

    async def update_permission(self, permission_id: int, **kwargs) -> dict:
        p = await PermissionDAO.update_permission(self.db, permission_id, kwargs.get("permission_name"), kwargs.get("permission_code"), kwargs.get("description"))
        if not p:
            raise ValueError("Permission not found")
        return self.permission_to_dict(p)

    async def delete_permission(self, permission_id: int) -> bool:
        ok = await PermissionDAO.delete_permission(self.db, permission_id)
        if not ok:
            raise ValueError("Permission not found")
        return ok

    async def assign_permission_to_role(self, role_id: int, permission_id: int) -> dict:
        if not await RoleDAO.get_by_id(self.db, role_id):
            raise ValueError("Role not found")
        if not await PermissionDAO.get_by_id(self.db, permission_id):
            raise ValueError("Permission not found")
        rel = await RolePermissionDAO.assign_permission(self.db, role_id, permission_id)
        return {"id": rel.id, "role_id": rel.role_id, "permission_id": rel.permission_id}

    async def remove_permission_from_role(self, role_id: int, permission_id: int) -> bool:
        return await RolePermissionDAO.remove_permission(self.db, role_id, permission_id)

    async def get_role_permissions(self, role_id: int) -> list[dict]:
        return [self.permission_to_dict(p) for p in await RolePermissionDAO.get_permissions_by_role(self.db, role_id)]

    async def bind_permission_menu(self, permission_id: int, menu_id: int) -> dict:
        if not await PermissionDAO.get_by_id(self.db, permission_id):
            raise ValueError("Permission not found")
        if not await MenuDAO.get_by_id(self.db, menu_id):
            raise ValueError("Menu not found")
        rel = await PermissionMenuDAO.bind_permission_menu(self.db, permission_id, menu_id)
        return {"id": rel.id, "permission_id": rel.permission_id, "menu_id": rel.menu_id}

    async def remove_permission_menu(self, permission_id: int, menu_id: int) -> bool:
        return await PermissionMenuDAO.remove_permission_menu(self.db, permission_id, menu_id)
