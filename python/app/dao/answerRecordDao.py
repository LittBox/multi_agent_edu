from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.answer_record import AnswerRecord

"""
答题记录数据访问对象（DAO，Data Access Object），提供对答题记录表的增删改查操作，包括创建答题记录、根据ID查询答题记录、根据用户ID查询答题记录列表、删除答题记录等功能。
答题记录DAO的主要职责包括：
1. 创建答题记录：根据用户ID、题目ID、知识点ID、用户答案、是否正确、答题质量等信息创建新的答题记录，并记录答题的开始时间和提交时间。
2. 根据ID查询答题记录：根据答题记录ID查询答题记录的详细信息，包括用户ID、题目ID、知识点ID、用户答案、是否正确、答题质量、答题开始时间、提交时间、答题耗时等信息。
3. 根据用户ID查询答题记录列表：根据用户ID查询该用户的所有答题记录，并返回一个列表，包含每条记录的详细信息。 
"""
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
