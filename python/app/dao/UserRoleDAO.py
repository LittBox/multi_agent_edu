from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.roleDao import RoleDAO
from app.dao.userDao import UserDAO
from app.db.models.role import Role
from app.db.models.user import User
from app.db.models.user_role import UserRole

"""
用户角色关联 DAO。
对应 user_roles 表：user_id 唯一，一个用户只绑定一个角色。
"""

class UserRoleDAO:
    @staticmethod
    async def create_user_role(db: AsyncSession, user_id: int, role_id: int) -> UserRole:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        db.add(user_role)
        await db.commit()
        await db.refresh(user_role)
        return user_role

    @staticmethod
    async def get_by_id(db: AsyncSession, id: int) -> UserRole | None:
        result = await db.execute(select(UserRole).where(UserRole.id == id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_role(db: AsyncSession, user_id: int) -> UserRole | None:
        result = await db.execute(select(UserRole).where(UserRole.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_role_name(db: AsyncSession, role_id: int) -> str | None:
        result = await db.execute(select(Role).where(Role.role_id == role_id))
        role = result.scalar_one_or_none()
        return role.role_name if role else None

    @staticmethod
    async def upsert_user_role(db: AsyncSession, user_id: int, role_id: int) -> UserRole:
        user_role = await UserRoleDAO.get_user_role(db, user_id)
        if user_role:
            user_role.role_id = role_id
            await db.commit()
            await db.refresh(user_role)
            return user_role
        return await UserRoleDAO.create_user_role(db, user_id, role_id)

    @staticmethod
    async def update_role(db: AsyncSession, user_id: int, role_name: str) -> UserRole:
        user = await UserDAO.get_by_id(db, user_id, include_deleted=True)
        if not user:
            raise ValueError("User not found")
        role = await RoleDAO.get_by_name(db, role_name)
        if not role:
            raise ValueError("Role not found")
        user_role = await UserRoleDAO.get_user_role(db, user_id)
        if not user_role:
            raise ValueError("UserRole relation not found")
        user.role = role.role_name
        user_role.role_id = role.role_id
        await db.commit()
        await db.refresh(user_role)
        return user_role

    @staticmethod
    async def assign_role_to_user(db: AsyncSession, user_id: int, role_name: str) -> UserRole:
        user = await UserDAO.get_by_id(db, user_id, include_deleted=True)
        if not user:
            raise ValueError("User not found")
        role = await RoleDAO.get_by_name(db, role_name)
        if not role:
            raise ValueError("Role not found")
        user.role = role.role_name
        return await UserRoleDAO.upsert_user_role(db, user_id, role.role_id)

    @staticmethod
    async def delete_user_role(db: AsyncSession, user_id: int) -> bool:
        user_role = await UserRoleDAO.get_user_role(db, user_id)
        if not user_role:
            return False
        await db.delete(user_role)
        await db.commit()
        return True

    @staticmethod
    async def get_users_by_role(db: AsyncSession, role_name: str) -> list[User]:
        role = await RoleDAO.get_by_name(db, role_name)
        if not role:
            raise ValueError("Role not found")
        result = await db.execute(
            select(User)
            .join(UserRole, UserRole.user_id == User.user_id)
            .where(UserRole.role_id == role.role_id)
            .order_by(User.user_id.asc())
        )
        return list(result.scalars().all())
