from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.student import Student

"""
学生 DAO，对应 students 表。
字段：student_id、user_id、student_no、student_name、major、grade、class_name、is_deleted。
"""

class StudentDAO:
    @staticmethod
    async def create_student(db: AsyncSession, user_id: int, student_no: str, student_name: str,
                             major: str | None = None, grade: int | None = None,
                             class_name: str | None = None) -> Student:
        student = Student(user_id=user_id, student_no=student_no, student_name=student_name,
                          major=major, grade=grade, class_name=class_name)
        db.add(student)
        await db.commit()
        await db.refresh(student)
        return student

    @staticmethod
    async def get_by_id(db: AsyncSession, student_id: int, include_deleted: bool = False) -> Student | None:
        conditions = [Student.student_id == student_id]
        if not include_deleted:
            conditions.append(Student.is_deleted == 0)
        result = await db.execute(select(Student).where(*conditions))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int, include_deleted: bool = False) -> Student | None:
        conditions = [Student.user_id == user_id]
        if not include_deleted:
            conditions.append(Student.is_deleted == 0)
        result = await db.execute(select(Student).where(*conditions))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_student_no(db: AsyncSession, student_no: str, include_deleted: bool = False) -> Student | None:
        conditions = [Student.student_no == student_no]
        if not include_deleted:
            conditions.append(Student.is_deleted == 0)
        result = await db.execute(select(Student).where(*conditions))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, major: str | None = None, grade: int | None = None,
                      class_name: str | None = None, include_deleted: bool = False) -> list[Student]:
        conditions = []
        if major is not None:
            conditions.append(Student.major == major)
        if grade is not None:
            conditions.append(Student.grade == grade)
        if class_name is not None:
            conditions.append(Student.class_name == class_name)
        if not include_deleted:
            conditions.append(Student.is_deleted == 0)
        stmt = select(Student)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await db.execute(stmt.order_by(Student.student_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_student(db: AsyncSession, student_id: int, student_no: str | None = None,
                             student_name: str | None = None, major: str | None = None,
                             grade: int | None = None, class_name: str | None = None,
                             is_deleted: int | None = None) -> Student | None:
        student = await StudentDAO.get_by_id(db, student_id, include_deleted=True)
        if not student:
            return None
        if student_no is not None:
            student.student_no = student_no
        if student_name is not None:
            student.student_name = student_name
        if major is not None:
            student.major = major
        if grade is not None:
            student.grade = grade
        if class_name is not None:
            student.class_name = class_name
        if is_deleted is not None:
            student.is_deleted = is_deleted
        student.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(student)
        return student

    @staticmethod
    async def soft_delete(db: AsyncSession, student_id: int) -> bool:
        student = await StudentDAO.get_by_id(db, student_id)
        if not student:
            return False
        student.is_deleted = 1
        student.updated_at = datetime.now(UTC)
        await db.commit()
        return True

    @staticmethod
    async def restore(db: AsyncSession, student_id: int) -> bool:
        student = await StudentDAO.get_by_id(db, student_id, include_deleted=True)
        if not student:
            return False
        student.is_deleted = 0
        student.updated_at = datetime.now(UTC)
        await db.commit()
        return True

    @staticmethod
    async def hard_delete(db: AsyncSession, student_id: int) -> bool:
        student = await StudentDAO.get_by_id(db, student_id, include_deleted=True)
        if not student:
            return False
        await db.delete(student)
        await db.commit()
        return True
