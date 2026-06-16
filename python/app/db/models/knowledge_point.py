from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class KnowledgePoint(Base):
    """
    知识点表。

    用于记录课程或学科下的知识点，例如：二叉树、搜索算法、进程管理等。
    parent_id 支持知识点树结构。
    """

    __tablename__ = "knowledge_points"

    # 知识点主键，自增。
    knowledge_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 知识点名称。
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # 所属科目，例如 数据结构、人工智能导论。
    subject: Mapped[str] = mapped_column(String(50), nullable=False)

    # 知识点描述。
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 父知识点 ID，可为空。
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("knowledge_points.knowledge_id"),
        nullable=True,
    )

    # 难度等级，数值越大表示越难。
    difficulty: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # 自关联关系：父知识点。
    parent = relationship("KnowledgePoint", remote_side=[knowledge_id], back_populates="children")

    # 自关联关系：子知识点。
    children = relationship("KnowledgePoint", back_populates="parent")

    # 该知识点下的题目。
    questions = relationship("Question", back_populates="knowledge_point")

    # 学习者状态。
    learner_states = relationship("LearnerState", back_populates="knowledge_point")

    # 复习计划。
    review_schedules = relationship("ReviewSchedule", back_populates="knowledge_point")

    # 答题记录。
    answer_records = relationship("AnswerRecord", back_populates="knowledge_point")
