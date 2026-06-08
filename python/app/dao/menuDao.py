from app.db.models import Menu
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

"""
Menu数据访问对象，控制对Menu模型的数据库操作
"""

class MenuDAO:
    def __init__(self, session):
        self.session = session

    def get_menu_by_id(self, menu_id):
        return self.session.query(Menu).filter_by(menu_id=menu_id).first()

    def get_all_menus(self):
        return self.session.query(Menu).all()

    @staticmethod
    async def create_menu(db: AsyncSession, menu_name, description=None):
        new_menu = Menu(menu_name=menu_name, description=description)
        db.add(new_menu)
        await db.commit()
        await db.refresh(new_menu)
        return new_menu

    @staticmethod
    async def update_menu(db: AsyncSession, menu_id, menu_name=None, description=None):
        menu = await db.execute(select(Menu).filter_by(menu_id=menu_id))
        menu = menu.scalar_one_or_none()
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
    async def delete_menu(db: AsyncSession, menu_id):
        menu = await db.execute(select(Menu).filter_by(menu_id=menu_id))
        menu = menu.scalar_one_or_none()
        if not menu:
            return False
        await db.delete(menu)
        await db.commit()
        return True