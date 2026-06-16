from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Student(Base):
    """
    学生表。

    说明：
    - student_id 是学生业务主键。
    - user_id 关联 users.user_id，用于把登录账号和学生档案绑定起来。
    """

    __tablename__ = "students"

    # 学生主键，自增。
    student_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 关联用户表，一个学生档案对应一个登录用户。
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True, nullable=False)

    # 学号，全局唯一。
    student_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # 学生姓名。
    student_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # 专业。
    major: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # 年级，例如 2026。
    grade: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # 行政班级名称，例如 计科一班。
    class_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

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

    user = relationship("User", back_populates="student")

    # 该学生的选课记录。
    enrollments = relationship("CourseEnrollment", back_populates="student")

    # 该学生的考试提交记录。
    exam_submits = relationship("ExamSubmit", back_populates="student")

    # 该学生的作业提交记录。
    task_submissions = relationship("TaskSubmission", back_populates="student")

    def __repr__(self) -> str:
        return (
            f"Student(student_id={self.student_id}, student_no='{self.student_no}', "
            f"student_name='{self.student_name}')"
        )
