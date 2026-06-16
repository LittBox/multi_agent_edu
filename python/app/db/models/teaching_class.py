from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TeachingClass(Base):
    """
    教学班表。

    一个课程可以开设多个教学班；一个教师也可以负责多个教学班。
    教学班用于承载选课、上课时间、容量控制等业务。
    """

    __tablename__ = "teaching_classes"

    # 教学班主键，自增。
    class_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 所属课程。
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.course_id"), nullable=False)

    # 授课教师。
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.teacher_id"), nullable=False)

    # 学期，例如 2026春季学期。
    semester: Mapped[str] = mapped_column(String(50), nullable=False)

    # 教学班名称，例如 数据结构-1班。
    class_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # 教学班容量，必须大于 0。
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    # 上课地点。
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # 当前已选课人数，需要小于等于 capacity。
    current_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 起始周。
    start_week: Mapped[int] = mapped_column(Integer, nullable=False)

    # 结束周。
    end_week: Mapped[int] = mapped_column(Integer, nullable=False)

    # 教学班状态：open / closed / cancelled / finished。
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")

    # 软删除标记：0 表示正常，1 表示删除。
    is_deleted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 上课时间安排，JSONB 数组，例如：
    # [
    #   {"weekday": 1, "start_time": "08:00", "end_time": "09:40"},
    #   {"weekday": 3, "start_time": "10:00", "end_time": "11:40"}
    # ]
    schedules: Mapped[list] = mapped_column(
        MutableList.as_mutable(JSONB),
        nullable=False,
        default=list,
    )

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

    course = relationship("Course", back_populates="teaching_classes")
    teacher = relationship("Teacher", back_populates="teaching_classes")

    # 当前教学班的选课记录。
    enrollments = relationship("CourseEnrollment", back_populates="teaching_class")

    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_class_capacity_positive"),
        CheckConstraint("current_count >= 0", name="ck_class_current_nonnegative"),
        CheckConstraint("current_count <= capacity", name="ck_class_current_within_capacity"),
        CheckConstraint("start_week > 0", name="ck_class_start_week_positive"),
        CheckConstraint("end_week >= start_week", name="ck_class_weeks"),
        CheckConstraint("status IN ('open', 'closed', 'cancelled', 'finished')", name="ck_class_status"),
    )
