from datetime import datetime, UTC

from sqlalchemy import DateTime, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# 学生表，记录学生基本信息，包括学号、姓名、专业、年级、班级等
class Student(Base):
    __tablename__ = "students"

    student_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 和用户表关联
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True, nullable=False)
    student_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    student_name: Mapped[str] = mapped_column(String(100), nullable=False)
    major: Mapped[str] = mapped_column(String(100), nullable=True)
    grade: Mapped[int] = mapped_column(Integer, nullable=True)
    class_name: Mapped[str] = mapped_column(String(100), nullable=True)
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

    user = relationship("User")

    def __repr__(self) -> str:
        return f"Student(student_id={self.student_id}, student_no='{self.student_no}', student_name='{self.student_name}', major='{self.major}', grade={self.grade}, class_name='{self.class_name}')"