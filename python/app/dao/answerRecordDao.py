from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.answer_record import AnswerRecord


class AnswerRecordDAO:

    @staticmethod
    async def create_answer_record(
        db: AsyncSession,
        user_id: int,
        question_id: int,
        knowledge_id: int,
        is_correct: bool,
        user_answer: str | None = None,
        quality_q: int | None = None,
        started_at: datetime | None = None,
        submitted_at: datetime | None = None,
        time_spent_seconds: float | None = None
    ) -> AnswerRecord:

        record = AnswerRecord(
            user_id=user_id,
            question_id=question_id,
            knowledge_id=knowledge_id,
            is_correct=is_correct,
            user_answer=user_answer,
            quality_q=quality_q,
            started_at=started_at,
            submitted_at=submitted_at,
            time_spent_seconds=time_spent_seconds
        )

        db.add(record)

        await db.commit()

        await db.refresh(record)

        return record

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        record_id: int
    ) -> AnswerRecord | None:

        result = await db.execute(
            select(AnswerRecord).where(
                AnswerRecord.record_id == record_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(
            select(AnswerRecord).where(
                AnswerRecord.user_id == user_id
            )
        )

        return result.scalars().all()

    @staticmethod
    async def delete_record(
        db: AsyncSession,
        record_id: int
    ) -> bool:

        record = await AnswerRecordDAO.get_by_id(
            db,
            record_id
        )

        if not record:
            return False

        await db.delete(record)

        await db.commit()

        return True
