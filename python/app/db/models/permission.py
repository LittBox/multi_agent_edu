from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Permission(Base):
    __tablename__ = "permissions"

    permission_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    permission_name: Mapped[str] = mapped_column(String(100), nullable=False)
    permission_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id"), nullable=False)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.permission_id"), nullable=False)

    role = relationship("Role")
    permission = relationship("Permission")

    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),)


class PermissionMenu(Base):
    __tablename__ = "permission_menus"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.permission_id"), nullable=False)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menus.menu_id"), nullable=False)

    permission = relationship("Permission")
    menu = relationship("Menu")

    __table_args__ = (UniqueConstraint("permission_id", "menu_id", name="uq_permission_menu"),)
