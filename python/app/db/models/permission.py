from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Permission(Base):
    """
    权限表。

    permission_code 建议使用稳定的英文编码，例如：
    - knowledge:view
    - course:manage
    - exam:submit
    """

    __tablename__ = "permissions"

    # 权限主键，自增。
    permission_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 权限中文名称。
    permission_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # 权限编码，全局唯一，用于后端鉴权判断。
    permission_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # 权限说明。
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    role_permissions = relationship("RolePermission", back_populates="permission")
    permission_menus = relationship("PermissionMenu", back_populates="permission")

    def __repr__(self) -> str:
        return (
            f"Permission(permission_id={self.permission_id}, "
            f"permission_code='{self.permission_code}')"
        )


class RolePermission(Base):
    """
    角色权限关联表。

    注意：你之前数据库报错中主键列名是 role_permission_id。
    所以下面使用 Python 属性名 id，实际映射到数据库列 role_permission_id。
    如果你的数据库最终已经把该列改成 id，请把 mapped_column("role_permission_id", ...)
    改成 mapped_column(primary_key=True, autoincrement=True)。
    """

    __tablename__ = "role_permissions"

    # 关联表主键。
    id: Mapped[int] = mapped_column("role_permission_id", primary_key=True, autoincrement=True)

    # 关联 roles.role_id。
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id"), nullable=False)

    # 关联 permissions.permission_id。
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.permission_id"), nullable=False)

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )


class PermissionMenu(Base):
    """
    权限菜单关联表。

    表示某个权限对应哪些前端菜单入口。
    """

    __tablename__ = "permission_menus"

    # 关联表主键。
    # 如果你的数据库列名是 permission_menu_id，可以改成：
    # id: Mapped[int] = mapped_column("permission_menu_id", primary_key=True, autoincrement=True)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 关联 permissions.permission_id。
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.permission_id"), nullable=False)

    # 关联 menus.menu_id。
    menu_id: Mapped[int] = mapped_column(ForeignKey("menus.menu_id"), nullable=False)

    permission = relationship("Permission", back_populates="permission_menus")
    menu = relationship("Menu", back_populates="permission_menus")

    __table_args__ = (
        UniqueConstraint("permission_id", "menu_id", name="uq_permission_menu"),
    )
