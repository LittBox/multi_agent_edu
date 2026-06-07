from datetime import datetime, UTC

from sqlalchemy import DateTime, ForeignKey, Boolean, Text, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

#答题记录表
class AnswerRecord(Base):
    __tablename__ = "answer_records"

    record_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.question_id"),
        nullable=False,
    )
    knowledge_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_points.knowledge_id"),
        nullable=False,
    )

    user_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)

    quality_q: Mapped[int | None] = mapped_column(Integer, nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    time_spent_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    user = relationship("User")
    question = relationship("Question")
    knowledge_point = relationship("KnowledgePoint")