from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import UTC, datetime
from app.db.base import Base


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
