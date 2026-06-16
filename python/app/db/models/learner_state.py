from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LearnerState(Base):
    """
    学习者知识点状态表。

    用于记录每个用户在每个知识点上的掌握情况，包括掌握度、练习次数、正确次数、连续正确次数等。
    user_id 关联 users.user_id，不是 students.student_id。
    """

    __tablename__ = "learner_states"

    # 学习状态主键，自增。
    state_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 用户 ID，关联 users.user_id。
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    # 知识点 ID。
    knowledge_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_points.knowledge_id"),
        nullable=False,
    )

    # 掌握度，通常范围 0~1。
    mastery: Mapped[float] = mapped_column(Float, default=0.2, nullable=False)

    # 学习率，影响掌握度更新速度。
    alpha: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # 遗忘率，影响遗忘模型。
    beta: Mapped[float] = mapped_column(Float, default=9.0, nullable=False)

    # 置信度，随着练习次数增加而提升。
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # 总练习次数。
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 正确次数。
    correct_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 连续正确次数。
    streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 最近一次练习时间。
    last_practiced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user = relationship("User")
    knowledge_point = relationship("KnowledgePoint", back_populates="learner_states")

    __table_args__ = (
        UniqueConstraint("user_id", "knowledge_id", name="uq_user_knowledge_state"),
    )
