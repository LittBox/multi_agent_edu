from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Question(Base):
    """
    题目表。

    支持单选题等题型。当前字段包含题干、A-D 选项、标准答案、解析、难度和图片地址。
    """

    __tablename__ = "questions"

    # 题目主键，自增。
    question_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 所属知识点，可为空。
    knowledge_id: Mapped[int | None] = mapped_column(
        ForeignKey("knowledge_points.knowledge_id"),
        nullable=True,
    )

    # 题型，例如 single_choice、multiple_choice、judge、short_answer。
    question_type: Mapped[str] = mapped_column(String(30), nullable=False)

    # 题干。
    stem: Mapped[str] = mapped_column(Text, nullable=False)

    # 选项 A-D。
    option_a: Mapped[str | None] = mapped_column(Text, nullable=True)
    option_b: Mapped[str | None] = mapped_column(Text, nullable=True)
    option_c: Mapped[str | None] = mapped_column(Text, nullable=True)
    option_d: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 标准答案，例如 A、B、TRUE，或简答题参考答案。
    answer: Mapped[str] = mapped_column(Text, nullable=False)

    # 答案解析。
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 题目难度。
    difficulty: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # 题目图片地址，可为空。
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=True,
    )

    knowledge_point = relationship("KnowledgePoint", back_populates="questions")

    # 题目被哪些考试引用。
    exam_questions = relationship("ExamQuestion", back_populates="question")

    # 该题目的答题记录。
    answer_records = relationship("AnswerRecord", back_populates="question")
