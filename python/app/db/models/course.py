from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Course(Base):
    """
    课程表。

    记录课程的基本信息，例如课程代码、课程名称、学分、课程描述、创建教师和课程状态。
    """

    __tablename__ = "courses"

    # 课程主键，自增。
    course_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 课程代码，全局唯一，例如 CS101。
    course_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # 课程名称，例如 数据结构。
    course_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # 学分，必须大于 0。
    credit: Mapped[float] = mapped_column(Float, nullable=False)

    # 课程描述。
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # 创建课程的教师。
    created_by_teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.teacher_id"),
        nullable=False,
    )

    # 课程状态：draft / active / closed。
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

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

    teacher = relationship("Teacher", back_populates="courses")

    # 课程下的教学班。
    teaching_classes = relationship("TeachingClass", back_populates="course")

    # 课程下的考试。
    exams = relationship("Exam", back_populates="course")

    # 课程下的作业。
    tasks = relationship("TaskBank", back_populates="course")

    __table_args__ = (
        CheckConstraint("credit > 0", name="ck_course_credit_positive"),
        CheckConstraint("status IN ('draft', 'active', 'closed')", name="ck_course_status"),
    )

    def __repr__(self) -> str:
        return (
            f"Course(course_id={self.course_id}, course_code='{self.course_code}', "
            f"course_name='{self.course_name}')"
        )
