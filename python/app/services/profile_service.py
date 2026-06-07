from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.userDao import UserDAO
from app.db.models.answer_record import AnswerRecord
from app.db.models.learner_state import LearnerState
from app.schemas.user_response import user_to_dict

MASTERY_MASTERED = 0.6

"""
档案服务类，主要职责包括：
1. 获取用户档案信息
2. 获取用户统计数据
3. 获取用户加入时间
"""
class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile(self, user_id: int) -> dict:
        user = await UserDAO.get_by_id(self.db, user_id)
        if not user:
            raise ValueError("User not found")

        total_answers = (
            await self.db.execute(
                select(func.count(AnswerRecord.record_id)).where(
                    AnswerRecord.user_id == user_id
                )
            )
        ).scalar_one()

        correct_answers = (
            await self.db.execute(
                select(func.count(AnswerRecord.record_id)).where(
                    AnswerRecord.user_id == user_id,
                    AnswerRecord.is_correct.is_(True),
                )
            )
        ).scalar_one()

        states = (
            await self.db.execute(
                select(LearnerState).where(LearnerState.user_id == user_id)
            )
        ).scalars().all()

        mastered = sum(1 for s in states if s.mastery >= MASTERY_MASTERED)

        return {
            "user": user_to_dict(user),
            "stats": {
                "total_answers": total_answers,
                "correct_answers": correct_answers,
                "accuracy": round(correct_answers / total_answers, 4)
                if total_answers
                else 0.0,
                "knowledge_points_tracked": len(states),
                "mastered_count": mastered,
            },
            "joined_at": user.created_at.isoformat(),
        }
