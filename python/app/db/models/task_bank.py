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


class TaskRelease(Base):
    """
    作业发布表。

    同一个作业内容可以被发布一次或多次，每次发布可以有不同截止时间。
    """

    __tablename__ = "task_releases"

    # 作业发布主键，自增。
    task_publish_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 作业库中的作业 ID。
    task_id: Mapped[int] = mapped_column(ForeignKey("task_bank.task_id"), nullable=False)

    # 发布时间。
    publish_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # 截止时间。
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

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

    task = relationship("TaskBank", back_populates="releases")

    # 学生提交记录。
    submissions = relationship("TaskSubmission", back_populates="release")


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
