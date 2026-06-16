from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Role(Base):
    """
    角色表。

    常见角色：
    - admin：管理员
    - teacher：教师
    - student：学生
    """

    __tablename__ = "roles"

    # 角色主键，自增。
    role_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 角色名称，例如 admin / teacher / student。
    role_name: Mapped[str] = mapped_column(String(20), nullable=False)

    # 关系：角色和用户的关联记录。
    user_roles = relationship("UserRole", back_populates="role")

    # 关系：角色可以访问哪些菜单。
    role_menus = relationship("RoleMenu", back_populates="role")

    # 关系：角色拥有的权限。
    role_permissions = relationship("RolePermission", back_populates="role")

    def __repr__(self) -> str:
        return f"Role(role_id={self.role_id}, role_name='{self.role_name}')"
