from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.role import Role

"""角色 DAO，对应 roles 表。"""

class RoleDAO:
    @staticmethod
    async def create_role(db: AsyncSession, role_name: str) -> Role:
        role = Role(role_name=role_name)
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role

    @staticmethod
    async def get_by_id(db: AsyncSession, role_id: int) -> Role | None:
        result = await db.execute(select(Role).where(Role.role_id == role_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, role_name: str) -> Role | None:
        result = await db.execute(select(Role).where(Role.role_name == role_name))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> list[Role]:
        result = await db.execute(select(Role).order_by(Role.role_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_role(db: AsyncSession, role_id: int, role_name: str) -> Role | None:
        role = await RoleDAO.get_by_id(db, role_id)
        if not role:
            return None
        role.role_name = role_name
        await db.commit()
        await db.refresh(role)
        return role

    @staticmethod
    async def delete_role(db: AsyncSession, role_id: int) -> bool:
        role = await RoleDAO.get_by_id(db, role_id)
        if not role:
            return False
        await db.delete(role)
        await db.commit()
        return True
