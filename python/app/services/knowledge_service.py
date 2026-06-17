"""知识仓库服务。

对应前端 KnowledgeWarehouseView：支持搜索、按 subject 筛选、加入个人知识仓库。
"""
from datetime import datetime, UTC

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.knowledgePointDao import KnowledgePointDAO
from app.dao.learnerStateDao import LearnerStateDAO
from app.dao.reviewScheduleDao import ReviewScheduleDAO
from app.db.models.knowledge_point import KnowledgePoint
from app.db.models.learner_state import LearnerState
from app.db.models.question import Question
from app.services._helpers import knowledge_to_dict
from app.core.learner_model import BKTParams, KnowledgeState, MasteryLevel




class KnowledgeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_knowledge_point(self, name: str, subject: str, description: str | None = None,
                                     parent_id: int | None = None, difficulty: int = 1) -> dict:
        if difficulty <= 0:
            raise ValueError("Difficulty must be positive")
        if parent_id is not None and not await KnowledgePointDAO.get_by_id(self.db, parent_id):
            raise ValueError("Parent knowledge point not found")
        kp = await KnowledgePointDAO.create_knowledge_point(self.db, name, subject, description, parent_id, difficulty)
        return knowledge_to_dict(kp)

    async def list_knowledge_points(self, q: str | None = None, subject: str | None = None) -> list[dict]:
        query = select(KnowledgePoint).order_by(KnowledgePoint.subject.asc(), KnowledgePoint.knowledge_id.asc())
        if subject:
            query = query.where(KnowledgePoint.subject == subject)
        if q:
            query = query.where(KnowledgePoint.name.ilike(f"%{q.strip()}%"))
        rows = (await self.db.execute(query)).scalars().all()
        return [knowledge_to_dict(item) for item in rows]

    async def get_repository(self, user_id: int, q: str | None = None, subject: str | None = None) -> dict:
        query = select(KnowledgePoint).order_by(KnowledgePoint.subject.asc(), KnowledgePoint.knowledge_id.asc())
        if subject:
            query = query.where(KnowledgePoint.subject == subject)
        if q:
            query = query.where(KnowledgePoint.name.ilike(f"%{q.strip()}%"))
        points = (await self.db.execute(query)).scalars().all()
        states = {s.knowledge_id: s for s in (await self.db.execute(select(LearnerState).where(LearnerState.user_id == user_id))).scalars().all()}
        count_rows = (await self.db.execute(select(Question.knowledge_id, func.count(Question.question_id)).group_by(Question.knowledge_id))).all()
        question_counts = {kid: count for kid, count in count_rows}

        def is_bkt_mastered(state: LearnerState | None) -> bool:
            if state is None:
                return False

            return KnowledgeState(
                knowledge_id=str(state.knowledge_id),
                mastery=state.mastery,
                attempts=state.attempts,
            ).level == MasteryLevel.MASTERED


        def parent_mastered(parent_id: int | None) -> bool:
            if parent_id is None:
                return True

            parent_state = states.get(parent_id)
            return is_bkt_mastered(parent_state)

        items = []
        for kp in points:
            state = states.get(kp.knowledge_id)
            mastery = state.mastery if state else 0.0
            attempts = state.attempts if state else 0
            if is_bkt_mastered(state):
                status = "mastered"
            elif not parent_mastered(kp.parent_id):
                status = "locked"
            elif attempts > 0:
                status = "learning"
            else:
                status = "not_started"
            items.append({
                **knowledge_to_dict(kp),
                "mastery": round(mastery, 2),
                "mastery_percent": int(round(mastery * 100)),
                "attempts": attempts,
                "streak": state.streak if state else 0,
                "status": status,
                "question_count": int(question_counts.get(kp.knowledge_id, 0)),
            })
        subjects = sorted({row[0] for row in (await self.db.execute(select(KnowledgePoint.subject).distinct())).all()})
        return {"items": items, "subjects": subjects, "total": len(items)}

    async def get_detail(self, knowledge_id: int, user_id: int | None = None) -> dict:
        kp = await KnowledgePointDAO.get_by_id(self.db, knowledge_id)
        if not kp:
            raise ValueError("Knowledge point not found")
        data = knowledge_to_dict(kp)
        if user_id is not None:
            state = await LearnerStateDAO.get_by_user_knowledge(self.db, user_id, knowledge_id)
            data["learning"] = {
                "mastery": round(state.mastery, 2),
                "mastery_percent": int(round(state.mastery * 100)),
                "attempts": state.attempts,
                "correct_attempts": state.correct_attempts,
                "streak": state.streak,
                "confidence": round(state.confidence, 2),
            } if state else None
        return data

    async def update_knowledge_point(self, knowledge_id: int, **kwargs) -> dict:
        allowed = {"name", "subject", "description", "parent_id", "difficulty"}
        data = {k: v for k, v in kwargs.items() if k in allowed}
        if data.get("difficulty") is not None and data["difficulty"] <= 0:
            raise ValueError("Difficulty must be positive")
        kp = await KnowledgePointDAO.update_knowledge_point(self.db, knowledge_id, **data)
        if not kp:
            raise ValueError("Knowledge point not found")
        return knowledge_to_dict(kp)

    async def delete_knowledge_point(self, knowledge_id: int) -> bool:
        ok = await KnowledgePointDAO.delete_knowledge_point(self.db, knowledge_id)
        if not ok:
            raise ValueError("Knowledge point not found")
        return ok

    async def join_point(self, knowledge_id: int, user_id: int) -> dict:
        kp = await KnowledgePointDAO.get_by_id(self.db, knowledge_id)
        if not kp:
            raise ValueError("Knowledge point not found")
        initial_state = KnowledgeState(
            knowledge_id=str(knowledge_id),
            mastery=BKTParams().p_init,
        )

        state = await LearnerStateDAO.upsert_state(
            self.db,
            user_id=user_id,
            knowledge_id=knowledge_id,
            mastery=initial_state.mastery,
            alpha=initial_state.alpha,
            beta=initial_state.beta,
            confidence=initial_state.confidence,
            attempts=initial_state.attempts,
            correct_attempts=initial_state.correct_count,
            streak=initial_state.streak,
        )
        await ReviewScheduleDAO.upsert_schedule(
            self.db,
            user_id=user_id,
            knowledge_id=knowledge_id,
            ef=2.5,
            interval_days=0,
            repetition=0,
            last_review_at=None,
            next_review_at=datetime.now(UTC),
        )
        return {"joined": True, "knowledge": knowledge_to_dict(kp), "state_id": state.state_id}
