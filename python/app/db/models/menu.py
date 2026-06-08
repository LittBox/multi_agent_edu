from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, String, Integer, Float, CheckConstraint
from app.db.base import Base


"""
菜单表，记录系统中的菜单信息，包括菜单名称、所属角色、描述等
"""
class Menu(Base):
    __tablename__ = "menus"


    menu_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    menu_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    
    def __repr__(self) -> str:
        return f"Menu(menu_id={self.menu_id}, menu_name='{self.menu_name}', description='{self.description}')"