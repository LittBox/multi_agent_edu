"""角色服务。"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.roleDao import RoleDAO
from app.dao.UserRoleDAO import UserRoleDAO


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def to_dict(role) -> dict:
        return {"role_id": role.role_id, "role_name": role.role_name}

    async def create_role(self, role_name: str) -> dict:
        if await RoleDAO.get_by_name(self.db, role_name):
            raise ValueError("Role already exists")
        return self.to_dict(await RoleDAO.create_role(self.db, role_name))

    async def list_roles(self) -> list[dict]:
        return [self.to_dict(r) for r in await RoleDAO.get_all(self.db)]

    async def update_role(self, role_id: int, role_name: str) -> dict:
        role = await RoleDAO.update_role(self.db, role_id, role_name)
        if not role:
            raise ValueError("Role not found")
        return self.to_dict(role)

    async def delete_role(self, role_id: int) -> bool:
        ok = await RoleDAO.delete_role(self.db, role_id)
        if not ok:
            raise ValueError("Role not found")
        return ok

    async def assign_role_to_user(self, user_id: int, role_name: str) -> dict:
        user_role = await UserRoleDAO.assign_role_to_user(self.db, user_id, role_name)
        return {"id": user_role.id, "user_id": user_role.user_id, "role_id": user_role.role_id}
