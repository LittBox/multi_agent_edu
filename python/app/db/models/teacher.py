from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Teacher(Base):
    """
    教师表。

    说明：
    - teacher_id 是教师业务主键。
    - user_id 关联 users.user_id，用于把登录账号和教师档案绑定起来。
    """

    __tablename__ = "teachers"

    # 教师主键，自增。
    teacher_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 关联用户表，一个教师档案对应一个登录用户。
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True, nullable=False)

    # 教师工号，全局唯一。
    teacher_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # 教师姓名。
    teacher_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # 所属院系。
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # 职称，例如 讲师、副教授、教授。
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # 软删除标记：0 表示正常，1 表示删除。
    is_deleted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user = relationship("User", back_populates="teacher")

    # 教师创建的课程。
    courses = relationship("Course", back_populates="teacher")

    # 教师负责的教学班。
    teaching_classes = relationship("TeachingClass", back_populates="teacher")

    # 教师创建的考试。
    exams = relationship("Exam", back_populates="teacher")

    # 教师创建的作业。
    tasks = relationship("TaskBank", back_populates="teacher")

    def __repr__(self) -> str:
        return (
            f"Teacher(teacher_id={self.teacher_id}, teacher_no='{self.teacher_no}', "
            f"teacher_name='{self.teacher_name}')"
        )
