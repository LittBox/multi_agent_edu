from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.knowledge_point import KnowledgePoint


"""
知识点数据访问对象（DAO，Data Access Object），提供对知识点表的增删改查操作，包括创建知识点、根据ID查询知识点、查询所有知识点、删除知识点等功能。
知识点DAO的主要职责包括：
1. 创建知识点：根据知识点名称、所属学科、描述信息、父知识点ID、难度等级等信息创建新的知识点记录，并检查知识点名称的唯一性。
2. 根据ID查询知识点：根据知识点ID查询知识点的详细信息，包括知识点名称、所属学科、描述信息、父知识点ID、难度等级等信息。
3. 查询所有知识点：查询所有知识点记录，并返回一个列表，包含每条记录的详细信息。
4. 删除知识点：根据知识点ID删除知识点记录
"""
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
