"""题库服务。"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.knowledgePointDao import KnowledgePointDAO
from app.dao.questionDao import QuestionDAO
from app.services._helpers import question_to_dict


class QuestionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_question(self, knowledge_id: int | None, question_type: str, stem: str, answer: str,
                              option_a: str | None = None, option_b: str | None = None,
                              option_c: str | None = None, option_d: str | None = None,
                              explanation: str | None = None, difficulty: int = 1,
                              image_url: str | None = None) -> dict:
        if knowledge_id is not None and not await KnowledgePointDAO.get_by_id(self.db, knowledge_id):
            raise ValueError("Knowledge point not found")
        if difficulty <= 0:
            raise ValueError("Difficulty must be positive")
        question = await QuestionDAO.create_question(self.db, knowledge_id, question_type, stem, answer,
                                                     option_a, option_b, option_c, option_d,
                                                     explanation, difficulty, image_url)
        return question_to_dict(question, include_answer=True)

    async def get_question(self, question_id: int, include_answer: bool = True) -> dict:
        question = await QuestionDAO.get_by_id(self.db, question_id)
        if not question:
            raise ValueError("Question not found")
        return question_to_dict(question, include_answer=include_answer)

    async def list_questions(self, knowledge_id: int | None = None, question_type: str | None = None,
                             difficulty: int | None = None, include_answer: bool = True) -> list[dict]:
        rows = await QuestionDAO.get_all(self.db, knowledge_id=knowledge_id, question_type=question_type, difficulty=difficulty)
        return [question_to_dict(item, include_answer=include_answer) for item in rows]

    async def update_question(self, question_id: int, **kwargs) -> dict:
        allowed = {"knowledge_id", "question_type", "stem", "option_a", "option_b", "option_c", "option_d", "answer", "explanation", "difficulty", "image_url"}
        data = {k: v for k, v in kwargs.items() if k in allowed}
        if data.get("knowledge_id") is not None and not await KnowledgePointDAO.get_by_id(self.db, data["knowledge_id"]):
            raise ValueError("Knowledge point not found")
        if data.get("difficulty") is not None and data["difficulty"] <= 0:
            raise ValueError("Difficulty must be positive")
        question = await QuestionDAO.update_question(self.db, question_id, **data)
        if not question:
            raise ValueError("Question not found")
        return question_to_dict(question, include_answer=True)

    async def delete_question(self, question_id: int) -> bool:
        ok = await QuestionDAO.delete_question(self.db, question_id)
        if not ok:
            raise ValueError("Question not found")
        return ok
