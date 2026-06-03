from datetime import datetime, UTC

from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    knowledge_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    subject: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("knowledge_points.knowledge_id"),
        nullable=True,
    )

    difficulty: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    parent = relationship("KnowledgePoint", remote_side=[knowledge_id])