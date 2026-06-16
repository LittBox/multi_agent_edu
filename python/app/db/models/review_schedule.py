from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReviewSchedule(Base):
    """
    复习计划表。

    用于记录每个用户在每个知识点上的间隔复习计划。
    user_id 关联 users.user_id，不是 students.student_id。
    """

    __tablename__ = "review_schedules"

    # 复习计划主键，自增。
    schedule_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 用户 ID。
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    # 知识点 ID。
    knowledge_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_points.knowledge_id"),
        nullable=False,
    )

    # easiness factor，记忆难易因子，SM-2 常用初始值为 2.5。
    ef: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)

    # 下次复习间隔天数。
    interval_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 已成功复习次数。
    repetition: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 上次复习时间。
    last_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # 下次复习时间。
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user = relationship("User")
    knowledge_point = relationship("KnowledgePoint", back_populates="review_schedules")

    __table_args__ = (
        UniqueConstraint("user_id", "knowledge_id", name="uq_user_knowledge_review"),
    )
