from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.teacher import Teacher

"""
教师数据访问对象
主要职责包括：
1. 创建教师
2. 根据ID查询教师
3. 根据用户ID查询教师
4. 根据教师工号查询教师
5. 查询所有教师
6. 更新教师信息
7. 删除教师
"""
class TeacherDAO:

    @staticmethod
    async def create_teacher(
        db: AsyncSession,
        user_id: int,
        teacher_no: str,
        teacher_name: str,
        department: str | None = None,
        title: str | None = None,
    ) -> Teacher:
        teacher = Teacher(
            user_id=user_id,
            teacher_no=teacher_no,
            teacher_name=teacher_name,
            department=department,
            title=title,
        )
        db.add(teacher)
        await db.commit()
        await db.refresh(teacher)
        return teacher

    @staticmethod
    async def get_by_id(db: AsyncSession, teacher_id: int) -> Teacher | None:
        result = await db.execute(
            select(Teacher).where(
                Teacher.teacher_id == teacher_id,
                Teacher.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> Teacher | None:
        result = await db.execute(
            select(Teacher).where(
                Teacher.user_id == user_id,
                Teacher.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_teacher_no(db: AsyncSession, teacher_no: str) -> Teacher | None:
        result = await db.execute(
            select(Teacher).where(
                Teacher.teacher_no == teacher_no,
                Teacher.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(
            select(Teacher).where(Teacher.is_deleted == 0)
        )
        return result.scalars().all()

    @staticmethod
    async def update_teacher(
        db: AsyncSession,
        teacher_id: int,
        **kwargs
    ) -> Teacher | None:
        teacher = await TeacherDAO.get_by_id(db, teacher_id)
        if not teacher:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(teacher, key):
                setattr(teacher, key, value)

        await db.commit()
        await db.refresh(teacher)
        return teacher

    @staticmethod
    async def soft_delete(db: AsyncSession, teacher_id: int) -> bool:
        teacher = await TeacherDAO.get_by_id(db, teacher_id)
        if not teacher:
            return False

        teacher.is_deleted = 1
        await db.commit()
        return True
