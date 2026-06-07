from datetime import datetime, UTC

from sqlalchemy import DateTime, ForeignKey, Float, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

#学习者状态表，记录每个学生在每个知识点上的掌握情况，包括掌握度、练习次数、正确次数、连续正确次数等信息
class LearnerState(Base):
    __tablename__ = "learner_states"

    state_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    knowledge_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_points.knowledge_id"),
        nullable=False,
    )

    """
    mastery，表示掌握度，初始值为0.2，每次练习后根据表现进行调整
    alpha，表示学习率，初始值为1.0，影响掌握度的更新速度
    beta，表示遗忘率，初始值为9.0，影响掌握度的遗忘速度
    """
    mastery: Mapped[float] = mapped_column(Float, default=0.2, nullable=False)

    alpha: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    beta: Mapped[float] = mapped_column(Float, default=9.0, nullable=False)

    """
    confidence，表示置信度，随着练习次数增加而增加，初始值为0.0，每次练习后根据表现进行调整
    attempts，表示练习次数，初始值为0，每次练习后加1
    correct_attempts，表示正确次数，初始值为0，每次练习正确后加1
    streak，表示连续正确次数，初始值为0，每次练习正确后加1，每次练习错误后重置为0
    """
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