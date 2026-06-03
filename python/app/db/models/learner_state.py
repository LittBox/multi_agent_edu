from datetime import datetime, UTC

from sqlalchemy import DateTime, ForeignKey, Float, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LearnerState(Base):
    __tablename__ = "learner_states"

    state_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    knowledge_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_points.knowledge_id"),
        nullable=False,
    )

    mastery: Mapped[float] = mapped_column(Float, default=0.2, nullable=False)

    alpha: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    beta: Mapped[float] = mapped_column(Float, default=9.0, nullable=False)

    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correct_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    last_practiced_at: Mapped[datetime | None] = mapped_column(
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
        UniqueConstraint("user_id", "knowledge_id", name="uq_user_knowledge_state"),
    )