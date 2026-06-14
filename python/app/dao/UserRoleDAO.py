from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.roleDao import RoleDAO
from app.dao.userDao import UserDAO
from app.db.models.user_role import UserRole
from app.db.models.user import User
from app.db.models.role import Role

class UserRoleDAO:

    @staticmethod
    async def get_user_role(db: AsyncSession, user_id: int):
        result = await db.execute(
            select(UserRole).where(UserRole.user_id == user_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_role_name(db: AsyncSession, role_id: int):
        result = await db.execute(
            select(Role).where(Role.role_id == role_id)
        )
        role = result.scalars().first()
        if not role:
            return None
        return role.role_name

    @staticmethod
    async def update_role(
        db: AsyncSession,
        user_id: int,
        role_name: str,
    ):
        # 判断用户是否存在
        user = await UserDAO.get_by_id(db, user_id)

        if not user:
            raise ValueError("User not found")

        # 判断角色是否存在
        role = await RoleDAO.get_by_name(
            db,
            role_name
        )

        if not role:
            raise ValueError("Role not found")

        # 判断用户角色关联是否存在
        result = await db.execute(
            select(UserRole).where(UserRole.user_id == user_id)
        )
        user_role = result.scalars().first()

        if not user_role:
            raise ValueError("UserRole relation not found")

        user_role.role_id = role.role_id

        await db.commit()
        await db.refresh(user_role)

        return user_role
    
    
    @staticmethod
    async def create_user_role(
        db: AsyncSession,
        user_id: int,
        role_id: int
    ):
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id
        )

        db.add(user_role)
        await db.commit()
        await db.refresh(user_role)

        return user_role
    
    @staticmethod
    async def assign_role_to_user(
        db: AsyncSession,
        user_id: int,
        role_name: str
    ):
        # 判断用户是否存在
        user = await UserDAO.get_by_id(db, user_id)

        if not user:
            raise ValueError("User not found")

        # 判断角色是否存在
        role = await RoleDAO.get_by_name(
            db,
            role_name
        )

        if not role:
            raise ValueError("Role not found")

        # 创建用户角色关联
        user_role = await UserRoleDAO.create_user_role(db, user_id=user_id, role_id=role.role_id)

        return user_role
    
    @staticmethod
    async def delete_user_role(
        db: AsyncSession,
        user_id: int,
    ):
        result = await db.execute(
            select(UserRole).where(UserRole.user_id == user_id)
        )
        user_role = result.scalars().first()

        if not user_role:
            raise ValueError("UserRole relation not found")

        await db.delete(user_role)
        await db.commit()

    @staticmethod
    async def get_users_by_role(
        db: AsyncSession,
        role_name: str
    ):
        # 判断角色是否存在
        role = await RoleDAO.get_by_name(
            db,
            role_name
        )

        if not role:
            raise ValueError("Role not found")

        result = await db.execute(
            select(User).join(UserRole).where(UserRole.role_id == role.role_id)
        )

        return result.scalars().all()