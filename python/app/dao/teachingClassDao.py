from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.teaching_class import TeachingClass

"""
教学班 DAO，对应 teaching_classes 表。
包含课程、教师、学期、班名、容量、地点、人数、周次、状态、schedules JSONB。
"""

class TeachingClassDAO:
    @staticmethod
    async def create_class(db: AsyncSession, course_id: int, teacher_id: int, semester: str,
                           schedules: list[dict], class_name: str, capacity: int,
                           start_week: int, end_week: int, location: str | None = None,
                           status: str = "open") -> TeachingClass:
        teaching_class = TeachingClass(course_id=course_id, teacher_id=teacher_id, semester=semester,
                                       class_name=class_name, capacity=capacity, current_count=0,
                                       schedules=schedules, start_week=start_week, end_week=end_week,
                                       location=location, status=status)
        db.add(teaching_class)
        await db.commit()
        await db.refresh(teaching_class)
        return teaching_class

    @staticmethod
    async def get_by_id(db: AsyncSession, class_id: int, include_deleted: bool = False) -> TeachingClass | None:
        conditions = [TeachingClass.class_id == class_id]
        if not include_deleted:
            conditions.append(TeachingClass.is_deleted == 0)
        result = await db.execute(select(TeachingClass).where(*conditions))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, status: str | None = None,
                      include_deleted: bool = False) -> list[TeachingClass]:
        conditions = []
        if status is not None:
            conditions.append(TeachingClass.status == status)
        if not include_deleted:
            conditions.append(TeachingClass.is_deleted == 0)
        stmt = select(TeachingClass)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await db.execute(stmt.order_by(TeachingClass.class_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_all_open(db: AsyncSession) -> list[TeachingClass]:
        return await TeachingClassDAO.get_all(db, status="open")

    @staticmethod
    async def get_by_teacher(db: AsyncSession, teacher_id: int, status: str | None = None,
                             include_deleted: bool = False) -> list[TeachingClass]:
        conditions = [TeachingClass.teacher_id == teacher_id]
        if status is not None:
            conditions.append(TeachingClass.status == status)
        if not include_deleted:
            conditions.append(TeachingClass.is_deleted == 0)
        result = await db.execute(select(TeachingClass).where(*conditions).order_by(TeachingClass.class_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_course(db: AsyncSession, course_id: int, status: str | None = None,
                            include_deleted: bool = False) -> list[TeachingClass]:
        conditions = [TeachingClass.course_id == course_id]
        if status is not None:
            conditions.append(TeachingClass.status == status)
        if not include_deleted:
            conditions.append(TeachingClass.is_deleted == 0)
        result = await db.execute(select(TeachingClass).where(*conditions).order_by(TeachingClass.class_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_semester(db: AsyncSession, semester: str, status: str | None = None,
                              include_deleted: bool = False) -> list[TeachingClass]:
        conditions = [TeachingClass.semester == semester]
        if status is not None:
            conditions.append(TeachingClass.status == status)
        if not include_deleted:
            conditions.append(TeachingClass.is_deleted == 0)
        result = await db.execute(select(TeachingClass).where(*conditions).order_by(TeachingClass.class_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_class(db: AsyncSession, class_id: int, **kwargs) -> TeachingClass | None:
        teaching_class = await TeachingClassDAO.get_by_id(db, class_id, include_deleted=True)
        if not teaching_class:
            return None
        allowed = {"course_id", "teacher_id", "semester", "class_name", "capacity", "location",
                   "current_count", "start_week", "end_week", "status", "is_deleted", "schedules"}
        for key, value in kwargs.items():
            if key in allowed and value is not None:
                setattr(teaching_class, key, value)
        teaching_class.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(teaching_class)
        return teaching_class

    @staticmethod
    async def update_status(db: AsyncSession, class_id: int, status: str) -> TeachingClass | None:
        return await TeachingClassDAO.update_class(db, class_id, status=status)

    @staticmethod
    async def can_enroll(db: AsyncSession, class_id: int) -> bool:
        teaching_class = await TeachingClassDAO.get_by_id(db, class_id)
        return bool(teaching_class and teaching_class.status == "open" and teaching_class.current_count < teaching_class.capacity)

    @staticmethod
    async def increment_count(db: AsyncSession, class_id: int) -> bool:
        teaching_class = await TeachingClassDAO.get_by_id(db, class_id)
        if not teaching_class or teaching_class.current_count >= teaching_class.capacity:
            return False
        teaching_class.current_count += 1
        teaching_class.updated_at = datetime.now(UTC)
        await db.commit()
        return True

    @staticmethod
    async def decrement_count(db: AsyncSession, class_id: int) -> bool:
        teaching_class = await TeachingClassDAO.get_by_id(db, class_id)
        if not teaching_class or teaching_class.current_count <= 0:
            return False
        teaching_class.current_count -= 1
        teaching_class.updated_at = datetime.now(UTC)
        await db.commit()
        return True

    @staticmethod
    async def soft_delete(db: AsyncSession, class_id: int) -> bool:
        teaching_class = await TeachingClassDAO.get_by_id(db, class_id)
        if not teaching_class:
            return False
        teaching_class.is_deleted = 1
        teaching_class.updated_at = datetime.now(UTC)
        await db.commit()
        return True
