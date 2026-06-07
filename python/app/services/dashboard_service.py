from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.answer_record import AnswerRecord
from app.db.models.knowledge_point import KnowledgePoint
from app.db.models.learner_state import LearnerState

MASTERY_MASTERED = 0.6
DEFAULT_MINUTES_PER_ANSWER = 3

"""
仪表板服务类，主要职责包括：
1. 获取仪表板摘要信息
2. 获取知识卡片信息
3. 获取学习路径信息
"""
class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_summary(self, user_id: int) -> dict:
        records = (
            await self.db.execute(
                select(AnswerRecord).where(AnswerRecord.user_id == user_id)
            )
        ).scalars().all()

        today = date.today()
        week_start = today - timedelta(days=6)

        def minutes_for(record: AnswerRecord) -> float:
            if record.time_spent_seconds:
                return record.time_spent_seconds / 60
            return DEFAULT_MINUTES_PER_ANSWER

        daily_minutes: dict[date, float] = {}
        for record in records:
            day = record.submitted_at.date()
            daily_minutes[day] = daily_minutes.get(day, 0) + minutes_for(record)

        trend = []
        for offset in range(6, -1, -1):
            day = today - timedelta(days=offset)
            trend.append(
                {
                    "date": day.isoformat(),
                    "minutes": round(daily_minutes.get(day, 0), 1),
                }
            )

        today_minutes = daily_minutes.get(today, 0)
        week_values = [daily_minutes.get(today - timedelta(days=i), 0) for i in range(7)]
        week_avg = sum(week_values) / 7

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
            "today_study_minutes": round(today_minutes, 1),
            "week_avg_minutes": round(week_avg, 1),
            "streak_days": streak,
            "trend": trend,
        }

    async def get_knowledge_cards(self, user_id: int) -> list[dict]:
        states = (
            await self.db.execute(
                select(LearnerState, KnowledgePoint)
                .join(
                    KnowledgePoint,
                    KnowledgePoint.knowledge_id == LearnerState.knowledge_id,
                )
                .where(LearnerState.user_id == user_id)
                .order_by(LearnerState.mastery.desc())
            )
        ).all()

        cards = []
        for state, kp in states:
            cards.append(
                {
                    "knowledge_id": kp.knowledge_id,
                    "name": kp.name,
                    "mastery": round(state.mastery, 2),
                    "mastery_percent": int(round(state.mastery * 100)),
                    "attempts": state.attempts,
                    "streak": state.streak,
                }
            )
        return cards

    async def get_learning_path(self, user_id: int) -> list[dict]:
        points = (
            await self.db.execute(
                select(KnowledgePoint).order_by(
                    KnowledgePoint.parent_id.asc().nullsfirst(),
                    KnowledgePoint.knowledge_id.asc(),
                )
            )
        ).scalars().all()

        states = {
            s.knowledge_id: s
            for s in (
                await self.db.execute(
                    select(LearnerState).where(LearnerState.user_id == user_id)
                )
            ).scalars().all()
        }

        def parent_mastered(parent_id: int | None) -> bool:
            if parent_id is None:
                return True
            parent_state = states.get(parent_id)
            return parent_state is not None and parent_state.mastery >= MASTERY_MASTERED

        path = []
        for kp in points:
            state = states.get(kp.knowledge_id)
            mastery = state.mastery if state else 0.0
            attempts = state.attempts if state else 0

            if mastery >= MASTERY_MASTERED:
                status = "done"
            elif not parent_mastered(kp.parent_id):
                status = "locked"
            elif attempts > 0:
                status = "learning"
            else:
                status = "locked"

            path.append(
                {
                    "knowledge_id": kp.knowledge_id,
                    "name": kp.name,
                    "status": status,
                    "mastery": round(mastery, 2),
                }
            )

        # 第一个已解锁但未掌握的知识点标为 learning
        for i, node in enumerate(path):
            if node["status"] == "locked":
                kp = points[i]
                if parent_mastered(kp.parent_id):
                    path[i] = {**node, "status": "learning"}
                    break

        return path

    async def get_agent_suggestions(self, user_id: int) -> dict:
        states = (
            await self.db.execute(
                select(LearnerState, KnowledgePoint)
                .join(
                    KnowledgePoint,
                    KnowledgePoint.knowledge_id == LearnerState.knowledge_id,
                )
                .where(LearnerState.user_id == user_id)
            )
        ).all()

        weak_name = "暂无薄弱知识点"
        weak_detail = "继续答题，系统将自动识别薄弱点"
        if states:
            weak_state, weak_kp = min(states, key=lambda row: row[0].mastery)
            weak_name = weak_kp.name
            weak_detail = f"掌握度 {int(weak_state.mastery * 100)}%，建议加强练习"

        next_name = "马克思主义基本原理"
        next_detail = "从基础知识点开始系统学习"
        path = await self.get_learning_path(user_id)
        for node in path:
            if node["status"] == "learning":
                next_name = node["name"]
                next_detail = f"建议学习《{node['name']}》"
                break

        summary = await self.get_dashboard_summary(user_id)
        streak = summary["streak_days"]
        encouragement = (
            f"你已经连续学习 {streak} 天了！"
            if streak > 0
            else "今天开始第一道题，开启你的学习之旅吧！"
        )

        return {
            "start_learning": {
                "title": "建议开始学习",
                "detail": next_detail,
                "knowledge_name": next_name,
            },
            "weak_point": {
                "title": "薄弱知识点",
                "detail": weak_detail,
                "knowledge_name": weak_name,
            },
            "encouragement": {
                "title": "鼓励建议",
                "detail": encouragement,
            },
        }
