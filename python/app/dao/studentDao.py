from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.student import Student

"""
学生数据访问对象
主要职责包括：
1. 创建学生
2. 根据ID查询学生
3. 根据用户ID查询学生
4. 根据学号查询学生
5. 查询所有学生
6. 更新学生信息
7. 删除学生
"""
class StudentDAO:

    @staticmethod
    async def create_student(
        db: AsyncSession,
        user_id: int,
        student_no: str,
        student_name: str,
        major: str | None = None,
        grade: int | None = None,
        class_name: str | None = None,
    ) -> Student:
        student = Student(
            user_id=user_id,
            student_no=student_no,
            student_name=student_name,
            major=major,
            grade=grade,
            class_name=class_name,
        )
        db.add(student)
        await db.commit()
        await db.refresh(student)
        return student

    @staticmethod
    async def get_by_id(db: AsyncSession, student_id: int) -> Student | None:
        result = await db.execute(
            select(Student).where(
                Student.student_id == student_id,
                Student.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> Student | None:
        result = await db.execute(
            select(Student).where(
                Student.user_id == user_id,
                Student.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_student_no(db: AsyncSession, student_no: str) -> Student | None:
        result = await db.execute(
            select(Student).where(
                Student.student_no == student_no,
                Student.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(
            select(Student).where(Student.is_deleted == 0)
        )
        return result.scalars().all()

    @staticmethod
    async def update_student(
        db: AsyncSession,
        student_id: int,
        **kwargs
    ) -> Student | None:
        student = await StudentDAO.get_by_id(db, student_id)
        if not student:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(student, key):
                setattr(student, key, value)

        await db.commit()
        await db.refresh(student)
        return student

    @staticmethod
    async def soft_delete(db: AsyncSession, student_id: int) -> bool:
        student = await StudentDAO.get_by_id(db, student_id)
        if not student:
            return False

        student.is_deleted = 1
        await db.commit()
        return True
