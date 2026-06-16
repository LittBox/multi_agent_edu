from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.knowledge_point import KnowledgePoint

"""知识点 DAO，对应 knowledge_points 表。"""

class KnowledgePointDAO:
    @staticmethod
    async def create_knowledge_point(db: AsyncSession, name: str, subject: str,
                                     description: str | None = None,
                                     parent_id: int | None = None,
                                     difficulty: int = 1) -> KnowledgePoint:
        knowledge_point = KnowledgePoint(name=name, subject=subject, description=description,
                                         parent_id=parent_id, difficulty=difficulty)
        db.add(knowledge_point)
        await db.commit()
        await db.refresh(knowledge_point)
        return knowledge_point

    @staticmethod
    async def get_by_id(db: AsyncSession, knowledge_id: int) -> KnowledgePoint | None:
        result = await db.execute(select(KnowledgePoint).where(KnowledgePoint.knowledge_id == knowledge_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_subject(db: AsyncSession, subject: str) -> list[KnowledgePoint]:
        result = await db.execute(select(KnowledgePoint).where(KnowledgePoint.subject == subject).order_by(KnowledgePoint.knowledge_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_children(db: AsyncSession, parent_id: int) -> list[KnowledgePoint]:
        result = await db.execute(select(KnowledgePoint).where(KnowledgePoint.parent_id == parent_id).order_by(KnowledgePoint.knowledge_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_all(db: AsyncSession, subject: str | None = None,
                      difficulty: int | None = None, keyword: str | None = None) -> list[KnowledgePoint]:
        conditions = []
        if subject is not None:
            conditions.append(KnowledgePoint.subject == subject)
        if difficulty is not None:
            conditions.append(KnowledgePoint.difficulty == difficulty)
        if keyword:
            conditions.append(KnowledgePoint.name.ilike(f"%{keyword.strip()}%"))
        stmt = select(KnowledgePoint)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await db.execute(stmt.order_by(KnowledgePoint.subject.asc(), KnowledgePoint.knowledge_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_knowledge_point(db: AsyncSession, knowledge_id: int, **kwargs) -> KnowledgePoint | None:
        knowledge_point = await KnowledgePointDAO.get_by_id(db, knowledge_id)
        if not knowledge_point:
            return None
        for key in ("name", "subject", "description", "parent_id", "difficulty"):
            if key in kwargs and kwargs[key] is not None:
                setattr(knowledge_point, key, kwargs[key])
        await db.commit()
        await db.refresh(knowledge_point)
        return knowledge_point

    @staticmethod
    async def delete_knowledge_point(db: AsyncSession, knowledge_id: int) -> bool:
        knowledge_point = await KnowledgePointDAO.get_by_id(db, knowledge_id)
        if not knowledge_point:
            return False
        await db.delete(knowledge_point)
        await db.commit()
        return True
