from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.menu import Menu
from app.db.models.role_menu import RoleMenu

"""角色菜单 DAO，对应 role_menus 表。"""

class RoleMenuDAO:
    @staticmethod
    async def bind_role_menu(db: AsyncSession, role_id: int, menu_id: int) -> RoleMenu:
        existed = await RoleMenuDAO.get_by_role_menu(db, role_id, menu_id)
        if existed:
            return existed
        role_menu = RoleMenu(role_id=role_id, menu_id=menu_id)
        db.add(role_menu)
        await db.commit()
        await db.refresh(role_menu)
        return role_menu

    @staticmethod
    async def get_by_id(db: AsyncSession, id: int) -> RoleMenu | None:
        result = await db.execute(select(RoleMenu).where(RoleMenu.id == id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_role_menu(db: AsyncSession, role_id: int, menu_id: int) -> RoleMenu | None:
        result = await db.execute(select(RoleMenu).where(RoleMenu.role_id == role_id, RoleMenu.menu_id == menu_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_role_id(db: AsyncSession, role_id: int) -> list[RoleMenu]:
        result = await db.execute(select(RoleMenu).where(RoleMenu.role_id == role_id).order_by(RoleMenu.id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_menus_by_role(db: AsyncSession, role_id: int) -> list[Menu]:
        result = await db.execute(
            select(Menu)
            .join(RoleMenu, RoleMenu.menu_id == Menu.menu_id)
            .where(RoleMenu.role_id == role_id)
            .order_by(Menu.menu_id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def unbind_role_menu(db: AsyncSession, role_id: int, menu_id: int) -> bool:
        role_menu = await RoleMenuDAO.get_by_role_menu(db, role_id, menu_id)
        if not role_menu:
            return False
        await db.delete(role_menu)
        await db.commit()
        return True

    @staticmethod
    async def delete_by_id(db: AsyncSession, id: int) -> bool:
        role_menu = await RoleMenuDAO.get_by_id(db, id)
        if not role_menu:
            return False
        await db.delete(role_menu)
        await db.commit()
        return True
