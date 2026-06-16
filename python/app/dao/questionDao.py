from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.question import Question

"""题目 DAO，对应 questions 表。"""

class QuestionDAO:
    @staticmethod
    async def create_question(db: AsyncSession, knowledge_id: int | None, question_type: str,
                              stem: str, answer: str, option_a: str | None = None,
                              option_b: str | None = None, option_c: str | None = None,
                              option_d: str | None = None, explanation: str | None = None,
                              difficulty: int = 1, image_url: str | None = None) -> Question:
        question = Question(knowledge_id=knowledge_id, question_type=question_type, stem=stem,
                            option_a=option_a, option_b=option_b, option_c=option_c,
                            option_d=option_d, answer=answer, explanation=explanation,
                            difficulty=difficulty, image_url=image_url)
        db.add(question)
        await db.commit()
        await db.refresh(question)
        return question

    @staticmethod
    async def get_by_id(db: AsyncSession, question_id: int) -> Question | None:
        result = await db.execute(select(Question).where(Question.question_id == question_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_knowledge(db: AsyncSession, knowledge_id: int) -> list[Question]:
        result = await db.execute(select(Question).where(Question.knowledge_id == knowledge_id).order_by(Question.question_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_all(db: AsyncSession, knowledge_id: int | None = None,
                      question_type: str | None = None, difficulty: int | None = None,
                      keyword: str | None = None) -> list[Question]:
        conditions = []
        if knowledge_id is not None:
            conditions.append(Question.knowledge_id == knowledge_id)
        if question_type is not None:
            conditions.append(Question.question_type == question_type)
        if difficulty is not None:
            conditions.append(Question.difficulty == difficulty)
        if keyword:
            conditions.append(Question.stem.ilike(f"%{keyword.strip()}%"))
        stmt = select(Question)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await db.execute(stmt.order_by(Question.question_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_question(db: AsyncSession, question_id: int, **kwargs) -> Question | None:
        question = await QuestionDAO.get_by_id(db, question_id)
        if not question:
            return None
        for key in ("knowledge_id", "question_type", "stem", "option_a", "option_b",
                    "option_c", "option_d", "answer", "explanation", "difficulty", "image_url"):
            if key in kwargs and kwargs[key] is not None:
                setattr(question, key, kwargs[key])
        await db.commit()
        await db.refresh(question)
        return question

    @staticmethod
    async def delete_question(db: AsyncSession, question_id: int) -> bool:
        question = await QuestionDAO.get_by_id(db, question_id)
        if not question:
            return False
        await db.delete(question)
        await db.commit()
        return True
