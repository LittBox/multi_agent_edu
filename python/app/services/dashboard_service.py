"""仪表板服务。"""
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.answer_record import AnswerRecord
from app.db.models.knowledge_point import KnowledgePoint
from app.db.models.learner_state import LearnerState
from app.core.learner_model import KnowledgeState, MasteryLevel

def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _is_mastered(state: LearnerState) -> bool:
        return (
            KnowledgeState(
                knowledge_id=str(state.knowledge_id),
                mastery=_safe_float(state.mastery),
                attempts=_safe_int(state.attempts),
                correct_count=_safe_int(state.correct_attempts),
                streak=_safe_int(state.streak),
                last_attempt=state.last_practiced_at,
            ).level
            == MasteryLevel.MASTERED
        )
    
    async def get_dashboard_summary(self, user_id: int) -> dict:
        records = (await self.db.execute(select(AnswerRecord).where(AnswerRecord.user_id == user_id))).scalars().all()
        today = date.today()
        daily_minutes: dict[date, float] = {}
        for record in records:
            day = record.submitted_at.date()
            seconds = float(record.time_spent_seconds or 0)
            if seconds > 0:
                daily_minutes[day] = daily_minutes.get(day, 0.0) + seconds / 60
        trend = [{"date": (today - timedelta(days=offset)).isoformat(), "minutes": round(daily_minutes.get(today - timedelta(days=offset), 0), 1)} for offset in range(6, -1, -1)]
        week_values = [daily_minutes.get(today - timedelta(days=i), 0) for i in range(7)]
        active_days = sorted({r.submitted_at.date() for r in records}, reverse=True)
        streak = 0
        cursor = today
        for day in active_days:
            if day == cursor:
                streak += 1
                cursor -= timedelta(days=1)
            elif day < cursor:
                break
        return {
            "today_study_minutes": round(daily_minutes.get(today, 0), 1),
            "week_avg_minutes": round(sum(week_values) / 7, 1),
            "streak_days": streak,
            "trend": trend,
        }

    async def get_knowledge_cards(self, user_id: int) -> list[dict]:
        rows = (await self.db.execute(select(LearnerState, KnowledgePoint).join(KnowledgePoint, KnowledgePoint.knowledge_id == LearnerState.knowledge_id).where(LearnerState.user_id == user_id).order_by(LearnerState.mastery.desc()))).all()
        return [{
            "knowledge_id": kp.knowledge_id,
            "name": kp.name,
            "subject": kp.subject,
            "mastery": round(state.mastery, 2),
            "mastery_percent": int(round(state.mastery * 100)),
            "attempts": state.attempts,
            "streak": state.streak,
            "status": "mastered" if self._is_mastered(state) else "learning"
        } for state, kp in rows]

    async def get_learning_path(self, user_id: int) -> list[dict]:
        points = (await self.db.execute(select(KnowledgePoint).order_by(KnowledgePoint.parent_id.asc().nullsfirst(), KnowledgePoint.knowledge_id.asc()))).scalars().all()
        states = {s.knowledge_id: s for s in (await self.db.execute(select(LearnerState).where(LearnerState.user_id == user_id))).scalars().all()}
        path = []
        for kp in points:
            state = states.get(kp.knowledge_id)
            mastery = state.mastery if state else 0.0
            attempts = state.attempts if state else 0
            if state and self._is_mastered(state):
                status = "done"
            elif attempts > 0:
                status = "learning"
            elif kp.parent_id:
                status = "locked"
            else:
                status = "available"
            path.append({"knowledge_id": kp.knowledge_id, "name": kp.name, "subject": kp.subject, "status": status, "mastery": round(mastery, 2)})
        return path
