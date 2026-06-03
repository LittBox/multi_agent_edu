from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.learner_state import LearnerState


class LearnerStateDAO:

    @staticmethod
    async def create_state(
        db: AsyncSession,
        user_id: int,
        knowledge_id: int,
        mastery: float | None = None,
        alpha: float | None = None,
        beta: float | None = None,
        confidence: float | None = None,
        attempts: int | None = None,
        correct_attempts: int | None = None,
        streak: int | None = None,
        last_practiced_at: datetime | None = None
    ) -> LearnerState:

        data: dict[str, object] = {
            "user_id": user_id,
            "knowledge_id": knowledge_id,
            "last_practiced_at": last_practiced_at
        }

        if mastery is not None:
            data["mastery"] = mastery

        if confidence is not None:
            data["confidence"] = confidence

        if attempts is not None:
            data["attempts"] = attempts

        if correct_attempts is not None:
            data["correct_attempts"] = correct_attempts

        if streak is not None:
            data["streak"] = streak

        state = LearnerState(**data)

        db.add(state)

        await db.commit()

        await db.refresh(state)

        return state

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        state_id: int
    ) -> LearnerState | None:

        result = await db.execute(
            select(LearnerState).where(
                LearnerState.state_id == state_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_knowledge(
        db: AsyncSession,
        user_id: int,
        knowledge_id: int
    ) -> LearnerState | None:

        result = await db.execute(
            select(LearnerState).where(
                LearnerState.user_id == user_id,
                LearnerState.knowledge_id == knowledge_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession
    ):

        result = await db.execute(
            select(LearnerState)
        )

        return result.scalars().all()

    @staticmethod
    async def delete_state(
        db: AsyncSession,
        state_id: int
    ) -> bool:

        state = await LearnerStateDAO.get_by_id(
            db,
            state_id
        )

        if not state:
            return False

        await db.delete(state)

        await db.commit()

        return True
    
    @staticmethod
    async def upsert_state(
        db,
        user_id,
        knowledge_id,
        mastery,
        alpha,
        beta,
        confidence,
        attempts,
        correct_attempts,
        streak,
        last_practiced_at=None
    ):
        state = await LearnerStateDAO.get_by_user_knowledge(
            db,
            user_id,
            knowledge_id
        )

        if state:
            state.mastery = mastery
            state.confidence = confidence
            state.alpha = alpha
            state.beta = beta
            state.attempts = attempts
            state.correct_attempts = correct_attempts
            state.streak = streak
            state.last_practiced_at = last_practiced_at

            await db.commit()
            await db.refresh(state)

            return state

        return await LearnerStateDAO.create_state(
            db=db,
            user_id=user_id,
            knowledge_id=knowledge_id,
            mastery=mastery,
            alpha=alpha,
            beta=beta,
            confidence=confidence,
            attempts=attempts,
            correct_attempts=correct_attempts,
            streak=streak,
            last_practiced_at=last_practiced_at,
        )
    
    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int):
        result = await db.execute(
            select(LearnerState).where(
                LearnerState.user_id == user_id
            )
        )

        return result.scalars().all()
