from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.knowledge_point import KnowledgePoint


class KnowledgePointDAO:

    @staticmethod
    async def create_knowledge_point(
        db: AsyncSession,
        name: str,
        subject: str,
        description: str | None = None,
        parent_id: int | None = None,
        difficulty: int = 1
    ) -> KnowledgePoint:

        knowledge_point = KnowledgePoint(
            name=name,
            subject=subject,
            description=description,
            parent_id=parent_id,
            difficulty=difficulty
        )

        db.add(knowledge_point)

        await db.commit()

        await db.refresh(knowledge_point)

        return knowledge_point

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        knowledge_id: int
    ) -> KnowledgePoint | None:

        result = await db.execute(
            select(KnowledgePoint).where(
                KnowledgePoint.knowledge_id == knowledge_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession
    ):

        result = await db.execute(
            select(KnowledgePoint)
        )

        return result.scalars().all()

    @staticmethod
    async def delete_knowledge_point(
        db: AsyncSession,
        knowledge_id: int
    ) -> bool:

        knowledge_point = await KnowledgePointDAO.get_by_id(
            db,
            knowledge_id
        )

        if not knowledge_point:
            return False

        await db.delete(knowledge_point)

        await db.commit()

        return True
