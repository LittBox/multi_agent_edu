from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.teacher import Teacher

"""
教师 DAO，对应 teachers 表。
字段：teacher_id、user_id、teacher_no、teacher_name、department、title、is_deleted。
"""

class TeacherDAO:
    @staticmethod
    async def create_teacher(db: AsyncSession, user_id: int, teacher_no: str, teacher_name: str,
                             department: str | None = None, title: str | None = None) -> Teacher:
        teacher = Teacher(user_id=user_id, teacher_no=teacher_no, teacher_name=teacher_name,
                          department=department, title=title)
        db.add(teacher)
        await db.commit()
        await db.refresh(teacher)
        return teacher

    @staticmethod
    async def get_by_id(db: AsyncSession, teacher_id: int, include_deleted: bool = False) -> Teacher | None:
        conditions = [Teacher.teacher_id == teacher_id]
        if not include_deleted:
            conditions.append(Teacher.is_deleted == 0)
        result = await db.execute(select(Teacher).where(*conditions))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int, include_deleted: bool = False) -> Teacher | None:
        conditions = [Teacher.user_id == user_id]
        if not include_deleted:
            conditions.append(Teacher.is_deleted == 0)
        result = await db.execute(select(Teacher).where(*conditions))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_teacher_no(db: AsyncSession, teacher_no: str, include_deleted: bool = False) -> Teacher | None:
        conditions = [Teacher.teacher_no == teacher_no]
        if not include_deleted:
            conditions.append(Teacher.is_deleted == 0)
        result = await db.execute(select(Teacher).where(*conditions))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, department: str | None = None,
                      title: str | None = None, include_deleted: bool = False) -> list[Teacher]:
        conditions = []
        if department is not None:
            conditions.append(Teacher.department == department)
        if title is not None:
            conditions.append(Teacher.title == title)
        if not include_deleted:
            conditions.append(Teacher.is_deleted == 0)
        stmt = select(Teacher)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await db.execute(stmt.order_by(Teacher.teacher_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_teacher(db: AsyncSession, teacher_id: int, teacher_no: str | None = None,
                             teacher_name: str | None = None, department: str | None = None,
                             title: str | None = None, is_deleted: int | None = None) -> Teacher | None:
        teacher = await TeacherDAO.get_by_id(db, teacher_id, include_deleted=True)
        if not teacher:
            return None
        if teacher_no is not None:
            teacher.teacher_no = teacher_no
        if teacher_name is not None:
            teacher.teacher_name = teacher_name
        if department is not None:
            teacher.department = department
        if title is not None:
            teacher.title = title
        if is_deleted is not None:
            teacher.is_deleted = is_deleted
        teacher.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(teacher)
        return teacher

    @staticmethod
    async def soft_delete(db: AsyncSession, teacher_id: int) -> bool:
        teacher = await TeacherDAO.get_by_id(db, teacher_id)
        if not teacher:
            return False
        teacher.is_deleted = 1
        teacher.updated_at = datetime.now(UTC)
        await db.commit()
        return True

    @staticmethod
    async def restore(db: AsyncSession, teacher_id: int) -> bool:
        teacher = await TeacherDAO.get_by_id(db, teacher_id, include_deleted=True)
        if not teacher:
            return False
        teacher.is_deleted = 0
        teacher.updated_at = datetime.now(UTC)
        await db.commit()
        return True

    @staticmethod
    async def hard_delete(db: AsyncSession, teacher_id: int) -> bool:
        teacher = await TeacherDAO.get_by_id(db, teacher_id, include_deleted=True)
        if not teacher:
            return False
        await db.delete(teacher)
        await db.commit()
        return True
