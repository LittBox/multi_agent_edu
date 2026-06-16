from __future__ import annotations

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RoleMenu(Base):
    """
    角色菜单关联表。

    表示某个角色可以看到或访问某个菜单。
    """

    __tablename__ = "role_menus"

    # 关联表主键，自增。
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 关联 roles.role_id。
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id"), nullable=False)

    # 关联 menus.menu_id。
    menu_id: Mapped[int] = mapped_column(ForeignKey("menus.menu_id"), nullable=False)

    role = relationship("Role", back_populates="role_menus")
    menu = relationship("Menu", back_populates="role_menus")

    __table_args__ = (
        UniqueConstraint("role_id", "menu_id", name="uq_role_menu"),
    )
