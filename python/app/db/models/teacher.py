from datetime import datetime, UTC

from sqlalchemy import DateTime, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# 教师表，记录教师基本信息，包括工号、姓名、院系、职称等
class Teacher(Base):
    __tablename__ = "teachers"

    teacher_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 和用户表关联
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True, nullable=False)
    teacher_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    teacher_name: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(String(100), nullable=True)
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
        return f"Teacher(teacher_id={self.teacher_id}, teacher_no='{self.teacher_no}', teacher_name='{self.teacher_name}', department='{self.department}', title='{self.title}')"
