from datetime import datetime, UTC

from sqlalchemy import DateTime, ForeignKey, String, Integer, Float, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

#课程表，记录课程基本信息，包括课程代码、课程名称、学分、课程描述、创建教师、课程状态等
class Course(Base):
    __tablename__ = "courses"

    course_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    course_name: Mapped[str] = mapped_column(String(200), nullable=False)
    credit: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by_teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.teacher_id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
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

    teacher = relationship("Teacher")

    __table_args__ = (
        CheckConstraint("credit > 0", name="ck_course_credit_positive"),
        CheckConstraint("status IN ('draft', 'active', 'closed')", name="ck_course_status"),
    )
