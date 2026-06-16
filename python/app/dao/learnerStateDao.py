from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.learner_state import LearnerState

"""
学习者状态 DAO，对应 learner_states 表。
user_id + knowledge_id 唯一；记录 mastery、alpha、beta、confidence、attempts、correct_attempts、streak。
"""

class LearnerStateDAO:
    @staticmethod
    async def create_state(db: AsyncSession, user_id: int, knowledge_id: int,
                           mastery: float | None = None, alpha: float | None = None,
                           beta: float | None = None, confidence: float | None = None,
                           attempts: int | None = None, correct_attempts: int | None = None,
                           streak: int | None = None,
                           last_practiced_at: datetime | None = None) -> LearnerState:
        data = {"user_id": user_id, "knowledge_id": knowledge_id}
        for key, value in {
            "mastery": mastery, "alpha": alpha, "beta": beta, "confidence": confidence,
            "attempts": attempts, "correct_attempts": correct_attempts,
            "streak": streak, "last_practiced_at": last_practiced_at,
        }.items():
            if value is not None:
                data[key] = value
        state = LearnerState(**data)
        db.add(state)
        await db.commit()
        await db.refresh(state)
        return state

    @staticmethod
    async def get_by_id(db: AsyncSession, state_id: int) -> LearnerState | None:
        result = await db.execute(select(LearnerState).where(LearnerState.state_id == state_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_knowledge(db: AsyncSession, user_id: int, knowledge_id: int) -> LearnerState | None:
        result = await db.execute(select(LearnerState).where(
            LearnerState.user_id == user_id,
            LearnerState.knowledge_id == knowledge_id,
        ))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> list[LearnerState]:
        result = await db.execute(select(LearnerState).where(LearnerState.user_id == user_id).order_by(LearnerState.knowledge_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_all(db: AsyncSession) -> list[LearnerState]:
        result = await db.execute(select(LearnerState).order_by(LearnerState.state_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_state(db: AsyncSession, state_id: int, **kwargs) -> LearnerState | None:
        state = await LearnerStateDAO.get_by_id(db, state_id)
        if not state:
            return None
        for key in ("mastery", "alpha", "beta", "confidence", "attempts",
                    "correct_attempts", "streak", "last_practiced_at"):
            if key in kwargs and kwargs[key] is not None:
                setattr(state, key, kwargs[key])
        state.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(state)
        return state

    @staticmethod
    async def upsert_state(db: AsyncSession, user_id: int, knowledge_id: int, mastery: float,
                           alpha: float, beta: float, confidence: float, attempts: int,
                           correct_attempts: int, streak: int,
                           last_practiced_at: datetime | None = None) -> LearnerState:
        state = await LearnerStateDAO.get_by_user_knowledge(db, user_id, knowledge_id)
        if state:
            state.mastery = mastery
            state.alpha = alpha
            state.beta = beta
            state.confidence = confidence
            state.attempts = attempts
            state.correct_attempts = correct_attempts
            state.streak = streak
            state.last_practiced_at = last_practiced_at
            state.updated_at = datetime.now(UTC)
            await db.commit()
            await db.refresh(state)
            return state
        return await LearnerStateDAO.create_state(db, user_id, knowledge_id, mastery, alpha, beta,
                                                  confidence, attempts, correct_attempts, streak,
                                                  last_practiced_at)

    @staticmethod
    async def delete_state(db: AsyncSession, state_id: int) -> bool:
        state = await LearnerStateDAO.get_by_id(db, state_id)
        if not state:
            return False
        await db.delete(state)
        await db.commit()
        return True
