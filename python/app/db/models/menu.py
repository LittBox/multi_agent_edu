from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Menu(Base):
    """
    菜单表。

    用于记录系统侧边栏、导航项或功能入口，例如：知识仓库、课程管理、考试管理等。
    """

    __tablename__ = "menus"

    # 菜单主键，自增。
    menu_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 菜单名称，全局唯一。
    menu_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # 菜单说明。
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # 关系：哪些角色可以访问该菜单。
    role_menus = relationship("RoleMenu", back_populates="menu")

    # 关系：哪些权限可以关联到该菜单。
    permission_menus = relationship("PermissionMenu", back_populates="menu")

    def __repr__(self) -> str:
        return f"Menu(menu_id={self.menu_id}, menu_name='{self.menu_name}')"
