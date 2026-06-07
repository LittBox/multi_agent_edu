from datetime import datetime, UTC

from sqlalchemy import DateTime, ForeignKey, Float, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

#复习计划表，记录每个学生在每个知识点上的复习计划，包括下次复习时间、复习间隔、复习次数等信息
class ReviewSchedule(Base):
    __tablename__ = "review_schedules"

    schedule_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    knowledge_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_points.knowledge_id"),
        nullable=False, 
    )

    """
    easiness factor，表示记忆的难易程度，初始值为2.5，每次复习后根据复习效果进行调整
    interval_days，表示下次复习的间隔天数，初始值为0，每次复习后根据复习效果进行调整
    repetition，表示已经复习的次数，初始值为0，每次复习成功后加1，每次复习失败后重置为0
    """
    ef: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    interval_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    repetition: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    last_review_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    next_review_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user = relationship("User")
    knowledge_point = relationship("KnowledgePoint")

    __table_args__ = (
        UniqueConstraint("user_id", "knowledge_id", name="uq_user_knowledge_review"),
    )