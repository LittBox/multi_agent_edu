from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import UTC, datetime
from app.db.base import Base


class TaskSubmission(Base):
    """
    作业提交表。

    记录学生针对某次作业发布的提交内容、得分和教师评语。
    """

    __tablename__ = "task_submissions"

    # 作业提交主键，自增。
    submit_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 作业发布 ID。
    task_publish_id: Mapped[int] = mapped_column(
        ForeignKey("task_releases.task_publish_id"),
        nullable=False,
    )

    # 学生 ID。
    student_id: Mapped[int] = mapped_column(ForeignKey("students.student_id"), nullable=False)

    # 提交时间。
    submit_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # 学生提交内容。
    answer_content: Mapped[str] = mapped_column(Text, nullable=False)

    # 作业得分。
    score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # 教师评语。
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

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

    release = relationship("TaskRelease", back_populates="submissions")
    student = relationship("Student", back_populates="task_submissions")

    __table_args__ = (
        UniqueConstraint("task_publish_id", "student_id", name="uq_task_submission_student"),
    )
