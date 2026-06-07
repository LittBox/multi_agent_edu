from datetime import datetime, UTC, date

from sqlalchemy import DateTime, ForeignKey, String, Integer, Date, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from app.db.base import Base

#教学班表，记录教学班信息，包括所属课程、授课教师、学期、班级名称、容量、当前人数、上课时间安排等
class TeachingClass(Base):
    __tablename__ = "teaching_classes"

    class_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    #一个课程可以有多个教学班，一个教师也可以有多个教学班
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.course_id"), nullable=False)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.teacher_id"), nullable=False)
    
    #学期和班级名称用于区分不同的教学班，例如“2024春季学期计算机科学与技术1班”、“2024秋季学期计算机科学与技术2班”等
    semester: Mapped[str] = mapped_column(String(50), nullable=False)
    class_name: Mapped[str] = mapped_column(String(100), nullable=False)
    #教学班容量和当前人数，用于控制选课人数，避免超额选课
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    #当前人数初始值为0，每当有学生选课成功时，当前人数加1；每当有学生退课成功时，当前人数减1
    current_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    start_week: Mapped[int] = mapped_column(Integer, nullable=False)
    end_week: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    is_deleted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
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

    #课程和教师的关系通过外键关联实现，可以通过relationship属性方便地访问教学班所属的课程和授课教师信息
    course = relationship("Course")
    teacher = relationship("Teacher")

    #数据库级别的约束条件，用于保证数据的合理性和一致性
    __table_args__ = (
        #课程容量必须大于0
        CheckConstraint("capacity > 0", name="ck_class_capacity_positive"),
        #当前人数必须大于或等于0，并且不能超过容量
        CheckConstraint("current_count >= 0", name="ck_class_current_nonnegative"),
        CheckConstraint("current_count <= capacity", name="ck_class_current_within_capacity"),
        CheckConstraint("start_week > 0", name="ck_class_start_week_positive"),
        CheckConstraint("end_week >= start_week", name="ck_class_weeks"),
        CheckConstraint("status IN ('open', 'closed', 'cancelled', 'finished')", name="ck_class_status"),
        #状态值必须在指定范围内
        CheckConstraint("status IN ('open', 'closed', 'cancelled', 'finished')", name="ck_class_status"),
    )
