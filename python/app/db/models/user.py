from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    """
    用户表。

    说明：
    - 保存系统登录账号的基础信息。
    - pwd 字段用于保存加密后的密码密文，不建议在业务代码中保存明文密码。
    - role 字段用于快速区分用户身份；更完整的权限控制通过 user_roles、roles、permissions 完成。
    """

    __tablename__ = "users"

    # 用户主键，自增。
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 登录用户名，全局唯一。
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # 密码密文，例如 bcrypt 哈希值。
    pwd: Mapped[str] = mapped_column(String(255), nullable=False)

    # 用户身份：admin / teacher / student。
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="student")

    # 用户邮箱，可为空。
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # 头像地址，可为空。
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # 用户状态：active / inactive / deleted。
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    # 创建时间。
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # 更新时间。
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # 关系：一个用户最多对应一条用户角色记录。
    user_role = relationship("UserRole", back_populates="user", uselist=False)

    # 关系：如果用户是学生，会在 students 表有一条记录。
    student = relationship("Student", back_populates="user", uselist=False)

    # 关系：如果用户是教师，会在 teachers 表有一条记录。
    teacher = relationship("Teacher", back_populates="user", uselist=False)

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'teacher', 'student')", name="ck_user_role"),
        CheckConstraint("status IN ('active', 'inactive', 'deleted')", name="ck_user_status"),
    )

    def __repr__(self) -> str:
        return (
            f"User(user_id={self.user_id}, username='{self.username}', "
            f"role='{self.role}', status='{self.status}')"
        )
