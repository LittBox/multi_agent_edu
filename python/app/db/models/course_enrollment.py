from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, String, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CourseEnrollment(Base):
    """
    学生选课表。

    记录学生选课、退课、退课原因和课程成绩等信息。
    注意：enroll_status 只允许 enrolled 和 dropped。
    """

    __tablename__ = "course_enrollments"

    # 选课记录主键，自增。
    enrollment_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 教学班 ID，关联 teaching_classes.class_id。
    class_id: Mapped[int] = mapped_column(ForeignKey("teaching_classes.class_id"), nullable=False)

    # 学生 ID，关联 students.student_id。
    student_id: Mapped[int] = mapped_column(ForeignKey("students.student_id"), nullable=False)

    # 选课状态：enrolled 表示已选课，dropped 表示已退课。
    enroll_status: Mapped[str] = mapped_column(String(20), nullable=False, default="enrolled")

    # 选课时间。
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # 退课时间，只有 enroll_status = dropped 时才有值。
    dropped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # 退课原因。
    drop_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # 课程成绩，可为空；退课记录通常为空。
    course_score: Mapped[float | None] = mapped_column(Float, nullable=True)

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

    teaching_class = relationship("TeachingClass", back_populates="enrollments")
    student = relationship("Student", back_populates="enrollments")

    __table_args__ = (
        CheckConstraint("enroll_status IN ('enrolled', 'dropped')", name="ck_enrollment_status"),
        # 同一个学生不能重复选同一个教学班；这里只限制未删除且状态为 enrolled 的记录。
        Index(
            "uq_student_class",
            "student_id",
            "class_id",
            unique=True,
            postgresql_where=and_(enroll_status == "enrolled", is_deleted == 0),
            sqlite_where=and_(enroll_status == "enrolled", is_deleted == 0),
        ),
    )
