from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.knowledgePointDao import KnowledgePointDAO
from app.db.models.knowledge_point import KnowledgePoint
from app.db.models.learner_state import LearnerState
from app.db.models.question import Question

MASTERY_MASTERED = 0.6

"""
知识服务类，主要职责包括：
1. 获取知识库信息
2. 获取知识详情
"""
class KnowledgeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_repository(
        self,
        user_id: int,
        q: str | None = None,
        subject: str | None = None,
    ) -> dict:
        query = select(KnowledgePoint).order_by(
            KnowledgePoint.subject.asc(),
            KnowledgePoint.knowledge_id.asc(),
        )

        if subject:
            query = query.where(KnowledgePoint.subject == subject)

        if q:
            query = query.where(KnowledgePoint.name.ilike(f"%{q.strip()}%"))

        points = (await self.db.execute(query)).scalars().all()

        states = {
            s.knowledge_id: s
            for s in (
                await self.db.execute(
                    select(LearnerState).where(LearnerState.user_id == user_id)
                )
            ).scalars().all()
        }

        count_rows = (
            await self.db.execute(
                select(Question.knowledge_id, func.count(Question.question_id))
                .group_by(Question.knowledge_id)
            )
        ).all()
        question_counts = {kid: count for kid, count in count_rows}

        def parent_mastered(parent_id: int | None) -> bool:
            if parent_id is None:
                return True
            parent = states.get(parent_id)
            return parent is not None and parent.mastery >= MASTERY_MASTERED

        items = []
        subjects: set[str] = set()

        for kp in points:
            subjects.add(kp.subject)
            state = states.get(kp.knowledge_id)
            mastery = state.mastery if state else 0.0
            attempts = state.attempts if state else 0

            if mastery >= MASTERY_MASTERED:
                status = "mastered"
            elif not parent_mastered(kp.parent_id):
                status = "locked"
            elif attempts > 0:
                status = "learning"
            else:
                status = "not_started"

            items.append(
                {
                    "knowledge_id": kp.knowledge_id,
                    "name": kp.name,
                    "subject": kp.subject,
                    "description": kp.description or "",
                    "difficulty": kp.difficulty,
                    "parent_id": kp.parent_id,
                    "mastery": round(mastery, 2),
                    "mastery_percent": int(round(mastery * 100)),
                    "attempts": attempts,
                    "streak": state.streak if state else 0,
                    "status": status,
                    "question_count": question_counts.get(kp.knowledge_id, 0),
                }
            )

        all_subjects = sorted(
            {
                row[0]
                for row in (
                    await self.db.execute(
                        select(KnowledgePoint.subject).distinct()
                    )
                ).all()
            }
        )

        return {
            "items": items,
            "subjects": all_subjects,
            "total": len(items),
        }

    async def get_detail(self, knowledge_id: int, user_id: int) -> dict:
        kp = await KnowledgePointDAO.get_by_id(self.db, knowledge_id)
        if not kp:
            raise ValueError("Knowledge point not found")

        repo = await self.get_repository(user_id)
        item = next(
            (i for i in repo["items"] if i["knowledge_id"] == knowledge_id),
            None,
        )

        return {
            "knowledge_id": kp.knowledge_id,
            "name": kp.name,
            "subject": kp.subject,
            "description": kp.description or "",
            "difficulty": kp.difficulty,
            "parent_id": kp.parent_id,
            "created_at": kp.created_at.isoformat(),
            "learning": item,
        }

    async def create_point(
        self,
        name: str,
        subject: str,
        description: str | None = None,
        parent_id: int | None = None,
        difficulty: int = 1,
    ):
        if parent_id is not None:
            parent = await KnowledgePointDAO.get_by_id(self.db, parent_id)
            if not parent:
                raise ValueError("Parent knowledge point not found")

        kp = await KnowledgePointDAO.create_knowledge_point(
            self.db,
            name=name,
            subject=subject,
            description=description,
            parent_id=parent_id,
            difficulty=difficulty,
        )
        return {
            "knowledge_id": kp.knowledge_id,
            "name": kp.name,
            "subject": kp.subject,
            "description": kp.description or "",
            "difficulty": kp.difficulty,
            "parent_id": kp.parent_id,
        }

    async def delete_point(self, knowledge_id: int) -> None:
        from app.db.models.question import Question

        question_count = (
            await self.db.execute(
                select(func.count(Question.question_id)).where(
                    Question.knowledge_id == knowledge_id
                )
            )
        ).scalar_one()

        if question_count > 0:
            raise ValueError(
                "Cannot delete knowledge point with existing questions"
            )

        deleted = await KnowledgePointDAO.delete_knowledge_point(
            self.db,
            knowledge_id,
        )
        if not deleted:
            raise ValueError("Knowledge point not found")
