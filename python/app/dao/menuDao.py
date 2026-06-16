from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.menu import Menu

"""菜单 DAO，对应 menus 表。"""

class MenuDAO:
    @staticmethod
    async def create_menu(db: AsyncSession, menu_name: str, description: str | None = None) -> Menu:
        menu = Menu(menu_name=menu_name, description=description)
        db.add(menu)
        await db.commit()
        await db.refresh(menu)
        return menu

    @staticmethod
    async def get_by_id(db: AsyncSession, menu_id: int) -> Menu | None:
        result = await db.execute(select(Menu).where(Menu.menu_id == menu_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, menu_name: str) -> Menu | None:
        result = await db.execute(select(Menu).where(Menu.menu_name == menu_name))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> list[Menu]:
        result = await db.execute(select(Menu).order_by(Menu.menu_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_menu(db: AsyncSession, menu_id: int, menu_name: str | None = None,
                          description: str | None = None) -> Menu | None:
        menu = await MenuDAO.get_by_id(db, menu_id)
        if not menu:
            return None
        if menu_name is not None:
            menu.menu_name = menu_name
        if description is not None:
            menu.description = description
        await db.commit()
        await db.refresh(menu)
        return menu

    @staticmethod
    async def delete_menu(db: AsyncSession, menu_id: int) -> bool:
        menu = await MenuDAO.get_by_id(db, menu_id)
        if not menu:
            return False
        await db.delete(menu)
        await db.commit()
        return True
