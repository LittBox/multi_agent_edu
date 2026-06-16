from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.answer_record import AnswerRecord

"""答题记录 DAO，对应 answer_records 表。"""

class AnswerRecordDAO:
    @staticmethod
    async def create_answer_record(db: AsyncSession, user_id: int, question_id: int,
                                   knowledge_id: int, is_correct: bool,
                                   user_answer: str | None = None, quality_q: int | None = None,
                                   started_at: datetime | None = None,
                                   submitted_at: datetime | None = None,
                                   time_spent_seconds: float | None = None) -> AnswerRecord:
        data = {"user_id": user_id, "question_id": question_id,
                "knowledge_id": knowledge_id, "is_correct": is_correct}
        for key, value in {"user_answer": user_answer, "quality_q": quality_q,
                           "started_at": started_at, "submitted_at": submitted_at,
                           "time_spent_seconds": time_spent_seconds}.items():
            if value is not None:
                data[key] = value
        record = AnswerRecord(**data)
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def get_by_id(db: AsyncSession, record_id: int) -> AnswerRecord | None:
        result = await db.execute(select(AnswerRecord).where(AnswerRecord.record_id == record_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> list[AnswerRecord]:
        result = await db.execute(select(AnswerRecord).where(AnswerRecord.user_id == user_id).order_by(AnswerRecord.created_at.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_question_id(db: AsyncSession, question_id: int) -> list[AnswerRecord]:
        result = await db.execute(select(AnswerRecord).where(AnswerRecord.question_id == question_id).order_by(AnswerRecord.created_at.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_knowledge_id(db: AsyncSession, knowledge_id: int) -> list[AnswerRecord]:
        result = await db.execute(select(AnswerRecord).where(AnswerRecord.knowledge_id == knowledge_id).order_by(AnswerRecord.created_at.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_user_knowledge(db: AsyncSession, user_id: int, knowledge_id: int) -> list[AnswerRecord]:
        result = await db.execute(select(AnswerRecord).where(
            AnswerRecord.user_id == user_id,
            AnswerRecord.knowledge_id == knowledge_id,
        ).order_by(AnswerRecord.created_at.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_record(db: AsyncSession, record_id: int, **kwargs) -> AnswerRecord | None:
        record = await AnswerRecordDAO.get_by_id(db, record_id)
        if not record:
            return None
        for key in ("user_answer", "is_correct", "quality_q", "started_at", "submitted_at", "time_spent_seconds"):
            if key in kwargs and kwargs[key] is not None:
                setattr(record, key, kwargs[key])
        await db.commit()
        await db.refresh(record)
        return record

    @staticmethod
    async def delete_record(db: AsyncSession, record_id: int) -> bool:
        record = await AnswerRecordDAO.get_by_id(db, record_id)
        if not record:
            return False
        await db.delete(record)
        await db.commit()
        return True
