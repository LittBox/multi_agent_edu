"""菜单服务。"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.menuDao import MenuDAO


class MenuService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def to_dict(menu) -> dict:
        return {"menu_id": menu.menu_id, "menu_name": menu.menu_name, "description": menu.description}

    async def create_menu(self, menu_name: str, description: str | None = None) -> dict:
        menu = await MenuDAO.create_menu(self.db, menu_name, description)
        return self.to_dict(menu)

    async def list_menus(self) -> list[dict]:
        return [self.to_dict(m) for m in await MenuDAO.get_all(self.db)]

    async def update_menu(self, menu_id: int, menu_name: str | None = None, description: str | None = None) -> dict:
        menu = await MenuDAO.update_menu(self.db, menu_id, menu_name, description)
        if not menu:
            raise ValueError("Menu not found")
        return self.to_dict(menu)

    async def delete_menu(self, menu_id: int) -> bool:
        ok = await MenuDAO.delete_menu(self.db, menu_id)
        if not ok:
            raise ValueError("Menu not found")
        return ok
