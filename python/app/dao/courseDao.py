from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.course import Course

"""
课程 DAO，对应 courses 表。
字段：course_code、course_name、credit、description、created_by_teacher_id、status、is_deleted。
"""

class CourseDAO:
    @staticmethod
    async def create_course(db: AsyncSession, course_code: str, course_name: str, credit: float,
                            created_by_teacher_id: int, description: str | None = None,
                            status: str = "active") -> Course:
        course = Course(course_code=course_code, course_name=course_name, credit=credit,
                        created_by_teacher_id=created_by_teacher_id, description=description, status=status)
        db.add(course)
        await db.commit()
        await db.refresh(course)
        return course

    @staticmethod
    async def get_by_id(db: AsyncSession, course_id: int, include_deleted: bool = False) -> Course | None:
        conditions = [Course.course_id == course_id]
        if not include_deleted:
            conditions.append(Course.is_deleted == 0)
        result = await db.execute(select(Course).where(*conditions))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_code(db: AsyncSession, course_code: str, include_deleted: bool = False) -> Course | None:
        conditions = [Course.course_code == course_code]
        if not include_deleted:
            conditions.append(Course.is_deleted == 0)
        result = await db.execute(select(Course).where(*conditions))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_teacher(db: AsyncSession, teacher_id: int, status: str | None = None,
                             include_deleted: bool = False) -> list[Course]:
        conditions = [Course.created_by_teacher_id == teacher_id]
        if status is not None:
            conditions.append(Course.status == status)
        if not include_deleted:
            conditions.append(Course.is_deleted == 0)
        result = await db.execute(select(Course).where(*conditions).order_by(Course.course_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_all(db: AsyncSession, status: str | None = None,
                      include_deleted: bool = False) -> list[Course]:
        conditions = []
        if status is not None:
            conditions.append(Course.status == status)
        if not include_deleted:
            conditions.append(Course.is_deleted == 0)
        stmt = select(Course)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await db.execute(stmt.order_by(Course.course_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_course(db: AsyncSession, course_id: int, course_code: str | None = None,
                            course_name: str | None = None, credit: float | None = None,
                            description: str | None = None, status: str | None = None,
                            is_deleted: int | None = None) -> Course | None:
        course = await CourseDAO.get_by_id(db, course_id, include_deleted=True)
        if not course:
            return None
        if course_code is not None:
            course.course_code = course_code
        if course_name is not None:
            course.course_name = course_name
        if credit is not None:
            course.credit = credit
        if description is not None:
            course.description = description
        if status is not None:
            course.status = status
        if is_deleted is not None:
            course.is_deleted = is_deleted
        course.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(course)
        return course

    @staticmethod
    async def update_status(db: AsyncSession, course_id: int, status: str) -> Course | None:
        return await CourseDAO.update_course(db, course_id, status=status)

    @staticmethod
    async def soft_delete(db: AsyncSession, course_id: int) -> bool:
        course = await CourseDAO.get_by_id(db, course_id)
        if not course:
            return False
        course.is_deleted = 1
        course.updated_at = datetime.now(UTC)
        await db.commit()
        return True

    @staticmethod
    async def restore(db: AsyncSession, course_id: int) -> bool:
        course = await CourseDAO.get_by_id(db, course_id, include_deleted=True)
        if not course:
            return False
        course.is_deleted = 0
        course.updated_at = datetime.now(UTC)
        await db.commit()
        return True
