"""个人档案服务。"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.studentDao import StudentDAO
from app.dao.teacherDao import TeacherDAO
from app.dao.userDao import UserDAO
from app.db.models.answer_record import AnswerRecord
from app.db.models.learner_state import LearnerState
from app.services._helpers import user_to_dict, student_to_dict, teacher_to_dict

MASTERY_MASTERED = 0.6


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile(self, user_id: int) -> dict:
        user = await UserDAO.get_by_id(self.db, user_id)
        if not user:
            raise ValueError("User not found")
        total = (await self.db.execute(select(func.count(AnswerRecord.record_id)).where(AnswerRecord.user_id == user_id))).scalar_one()
        correct = (await self.db.execute(select(func.count(AnswerRecord.record_id)).where(AnswerRecord.user_id == user_id, AnswerRecord.is_correct.is_(True)))).scalar_one()
        states = (await self.db.execute(select(LearnerState).where(LearnerState.user_id == user_id))).scalars().all()
        profile = None
        if user.role == "student":
            student = await StudentDAO.get_by_user_id(self.db, user_id)
            profile = student_to_dict(student) if student else None
        elif user.role == "teacher":
            teacher = await TeacherDAO.get_by_user_id(self.db, user_id)
            profile = teacher_to_dict(teacher) if teacher else None
        return {
            "user": user_to_dict(user),
            "profile": profile,
            "stats": {
                "total_answers": total,
                "correct_answers": correct,
                "accuracy": round(correct / total, 4) if total else 0.0,
                "joined_knowledge_count": len(states),
                "mastered_count": sum(1 for s in states if s.mastery >= MASTERY_MASTERED),
            },
        }

    async def update_profile(self, user_id: int, **kwargs) -> dict:
        user = await UserDAO.update_user(
            self.db,
            user_id,
            username=kwargs.get("username"),
            email=kwargs.get("email"),
            avatar=kwargs.get("avatar"),
        )
        if not user:
            raise ValueError("User not found")
        return await self.get_profile(user_id)
