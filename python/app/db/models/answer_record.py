from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AnswerRecord(Base):
    """
    答题记录表。

    记录用户每一次练习或答题行为，包括用户答案、是否正确、答题质量、耗时等。
    user_id 关联 users.user_id，不是 students.student_id。
    """

    __tablename__ = "answer_records"

    # 答题记录主键，自增。
    record_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 用户 ID。
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    # 题目 ID。
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.question_id"),
        nullable=False,
    )

    # 知识点 ID，冗余保存便于按知识点统计。
    knowledge_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_points.knowledge_id"),
        nullable=False,
    )

    # 用户提交的答案。
    user_answer: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 是否答对。
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # 答题质量评分，例如 SM-2 中 0~5 的质量评分。
    quality_q: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # 开始答题时间。
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # 提交时间。
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # 答题耗时，单位秒。
    time_spent_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    user = relationship("User")
    question = relationship("Question", back_populates="answer_records")
    knowledge_point = relationship("KnowledgePoint", back_populates="answer_records")
