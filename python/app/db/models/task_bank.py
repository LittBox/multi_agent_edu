from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TaskBank(Base):
    """
    作业库表。

    教师可以在作业库中维护作业内容，再通过 task_releases 发布给学生。
    """

    __tablename__ = "task_bank"

    # 作业主键，自增。
    task_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 所属课程。
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.course_id"), nullable=False)

    # 创建作业的教师。
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.teacher_id"), nullable=False)

    # 作业类型，例如 homework。
    task_type: Mapped[str] = mapped_column(String(30), nullable=False, default="homework")

    # 作业内容。
    task_content: Mapped[str] = mapped_column(Text, nullable=False)

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

    course = relationship("Course", back_populates="tasks")
    teacher = relationship("Teacher", back_populates="tasks")

    # 作业发布记录。
    releases = relationship("TaskRelease", back_populates="task")




