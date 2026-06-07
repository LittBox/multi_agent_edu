from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.question import Question

"""
题库数据访问对象（DAO，Data Access Object），提供对题库表的增删改查操作，包括创建题目、根据ID查询题目、查询所有题目、删除题目等功能。
题库DAO的主要职责包括：
1. 创建题目
2. 根据ID查询题目
3. 查询所有题目
4. 删除题目
"""
class QuestionDAO:

    @staticmethod
    async def create_question(
        db: AsyncSession,
        knowledge_id: int,
        question_type: str,
        stem: str,
        answer: str,
        option_a: str | None = None,
        option_b: str | None = None,
        option_c: str | None = None,
        option_d: str | None = None,
        explanation: str | None = None,
        difficulty: int = 1,
        image_url: str | None = None
    ) -> Question:

        question = Question(
            knowledge_id=knowledge_id,
            question_type=question_type,
            stem=stem,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            answer=answer,
            explanation=explanation,
            difficulty=difficulty,
            image_url=image_url
        )

        db.add(question)

        await db.commit()

        await db.refresh(question)

        return question

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        question_id: int
    ) -> Question | None:

        result = await db.execute(
            select(Question).where(
                Question.question_id == question_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession
    ):

        result = await db.execute(
            select(Question)
        )

        return result.scalars().all()

    @staticmethod
    async def delete_question(
        db: AsyncSession,
        question_id: int
    ) -> bool:

        question = await QuestionDAO.get_by_id(
            db,
            question_id
        )

        if not question:
            return False

        await db.delete(question)

        await db.commit()

        return True
