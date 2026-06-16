"""学习报告服务。"""
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.answer_record import AnswerRecord
from app.db.models.knowledge_point import KnowledgePoint
from app.db.models.learner_state import LearnerState

MASTERY_MASTERED = 0.6


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_learning_report(self, user_id: int) -> dict:
        records = (await self.db.execute(select(AnswerRecord).where(AnswerRecord.user_id == user_id).order_by(AnswerRecord.submitted_at.desc()))).scalars().all()
        states = (await self.db.execute(select(LearnerState, KnowledgePoint).join(KnowledgePoint, KnowledgePoint.knowledge_id == LearnerState.knowledge_id).where(LearnerState.user_id == user_id))).all()
        total = len(records)
        correct = sum(1 for r in records if r.is_correct)
        subject_stats: dict[str, dict] = {}
        for state, kp in states:
            bucket = subject_stats.setdefault(kp.subject, {"subject": kp.subject, "count": 0, "avg_mastery": 0.0})
            bucket["count"] += 1
            bucket["avg_mastery"] += state.mastery
        for bucket in subject_stats.values():
            bucket["avg_mastery"] = round(bucket["avg_mastery"] / bucket["count"], 2) if bucket["count"] else 0
        today = date.today()
        daily_accuracy = []
        for offset in range(6, -1, -1):
            day = today - timedelta(days=offset)
            day_records = [r for r in records if r.submitted_at.date() == day]
            day_total = len(day_records)
            day_correct = sum(1 for r in day_records if r.is_correct)
            daily_accuracy.append({"date": day.isoformat(), "total": day_total, "correct": day_correct, "accuracy": round(day_correct / day_total, 4) if day_total else 0.0})
        return {
            "summary": {
                "total_answers": total,
                "correct_answers": correct,
                "accuracy": round(correct / total, 4) if total else 0.0,
                "mastered_count": sum(1 for s, _ in states if s.mastery >= MASTERY_MASTERED),
                "learning_count": sum(1 for s, _ in states if s.attempts > 0 and s.mastery < MASTERY_MASTERED),
            },
            "weak_points": sorted([{"knowledge_id": kp.knowledge_id, "name": kp.name, "subject": kp.subject, "mastery": round(s.mastery, 2), "mastery_percent": int(round(s.mastery * 100)), "attempts": s.attempts} for s, kp in states], key=lambda x: x["mastery"])[:5],
            "subject_stats": list(subject_stats.values()),
            "daily_accuracy": daily_accuracy,
        }
