from __future__ import annotations

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(Base):
    """
    用户角色关联表。

    当前设计是一个用户只绑定一个角色，因此 user_id 设置为唯一。
    如果未来需要一个用户拥有多个角色，可以去掉 user_id 的 unique 约束，
    改用 UniqueConstraint(user_id, role_id)。
    """

    __tablename__ = "user_roles"

    # 关联表主键，自增。
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 关联 users.user_id。
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    # 关联 roles.role_id。
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id"), nullable=False)

    user = relationship("User", back_populates="user_role")
    role = relationship("Role", back_populates="user_roles")

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_role_user"),
    )
