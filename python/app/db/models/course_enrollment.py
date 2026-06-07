from datetime import datetime, UTC

from sqlalchemy import DateTime, ForeignKey, String, Integer, CheckConstraint, Index, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

#课程选课表，记录学生选课信息，包括选课状态、选课时间、退课时间和退课原因等
class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"

    enrollment_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("teaching_classes.class_id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.student_id"), nullable=False)
    #选课状态包括“enrolled”（已选课）和“dropped”（已退课），默认值为“enrolled”
    enroll_status: Mapped[str] = mapped_column(String(20), nullable=False, default="enrolled")
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    #退课时间，当选课状态为“dropped”时，该字段记录退课时间
    dropped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    drop_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
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

    teaching_class = relationship("TeachingClass")
    student = relationship("Student")

    __table_args__ = (
        CheckConstraint("enroll_status IN ('enrolled', 'dropped')", name="ck_enrollment_status"),
        Index(
            "uq_student_class",
            "student_id",
            "class_id",
            unique=True,
            postgresql_where=and_(enroll_status == "enrolled", is_deleted == 0),
            sqlite_where=and_(enroll_status == "enrolled", is_deleted == 0),
        ),
    )
