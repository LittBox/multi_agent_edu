from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.db.models.teaching_class import TeachingClass

"""
教学班数据访问对象
主要职责包括：
1. 创建教学班
2. 根据ID查询教学班
3. 根据教师ID查询教学班列表
4. 根据课程ID查询教学班列表
5. 根据学期查询教学班列表
6. 根据教师ID和学期查询教学班列表
7. 查询所有开放的教学班列表
8. 查询所有教学班列表
9. 更新教学班状态
10. 更新教学班信息
11. 增加教学班当前选课人数
12. 减少教学班当前选课人数
13. 删除教学班"""
class TeachingClassDAO:

    @staticmethod
    async def create_class(
        db: AsyncSession,
        course_id: int,
        teacher_id: int,
        semester: str,
        schedules: list[dict],
        class_name: str,
        capacity: int,
        start_week: int,
        end_week: int,
        location: str | None = None,
        status: str = "open",
    ) -> TeachingClass:
        teaching_class = TeachingClass(
            course_id=course_id,
            teacher_id=teacher_id,
            semester=semester,
            class_name=class_name,
            capacity=capacity,
            current_count=0,
            schedules=schedules,
            start_week=start_week,
            end_week=end_week,
            location=location,
            status=status,
        )
        db.add(teaching_class)
        await db.commit()
        await db.refresh(teaching_class)
        return teaching_class

    @staticmethod
    async def get_by_id(db: AsyncSession, class_id: int) -> TeachingClass | None:
        result = await db.execute(
            select(TeachingClass).where(
                TeachingClass.class_id == class_id,
                TeachingClass.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_teacher(db: AsyncSession, teacher_id: int):
        result = await db.execute(
            select(TeachingClass).where(
                TeachingClass.teacher_id == teacher_id,
                TeachingClass.is_deleted == 0
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_course(db: AsyncSession, course_id: int):
        result = await db.execute(
            select(TeachingClass).where(
                TeachingClass.course_id == course_id,
                TeachingClass.is_deleted == 0
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_semester(db: AsyncSession, semester: str):
        result = await db.execute(
            select(TeachingClass).where(
                TeachingClass.semester == semester,
                TeachingClass.is_deleted == 0
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_teacher_semester(db: AsyncSession, teacher_id: int, semester: str):
        result = await db.execute(
            select(TeachingClass).where(
                TeachingClass.teacher_id == teacher_id,
                TeachingClass.semester == semester,
                TeachingClass.is_deleted == 0
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_open(db: AsyncSession):
        result = await db.execute(
            select(TeachingClass).where(
                TeachingClass.status == "open",
                TeachingClass.is_deleted == 0
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(
            select(TeachingClass).where(TeachingClass.is_deleted == 0)
        )
        return result.scalars().all()

    @staticmethod
    async def update_status(db: AsyncSession, class_id: int, status: str) -> TeachingClass | None:
        teaching_class = await TeachingClassDAO.get_by_id(db, class_id)
        if not teaching_class:
            return None

        teaching_class.status = status
        await db.commit()
        await db.refresh(teaching_class)
        return teaching_class

    @staticmethod
    async def update_class(db: AsyncSession, class_id: int, **kwargs) -> TeachingClass | None:
        teaching_class = await TeachingClassDAO.get_by_id(db, class_id)
        if not teaching_class:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(teaching_class, key):
                setattr(teaching_class, key, value)

        await db.commit()
        await db.refresh(teaching_class)
        return teaching_class

    @staticmethod
    async def increment_count(db: AsyncSession, class_id: int) -> bool:
        teaching_class = await TeachingClassDAO.get_by_id(db, class_id)
        if not teaching_class or teaching_class.current_count >= teaching_class.capacity:
            return False

        teaching_class.current_count += 1
        await db.commit()
        return True

    @staticmethod
    async def decrement_count(db: AsyncSession, class_id: int) -> bool:
        teaching_class = await TeachingClassDAO.get_by_id(db, class_id)
        if not teaching_class or teaching_class.current_count <= 0:
            return False

        teaching_class.current_count -= 1
        await db.commit()
        return True

    @staticmethod
    async def soft_delete(db: AsyncSession, class_id: int) -> bool:
        teaching_class = await TeachingClassDAO.get_by_id(db, class_id)
        if not teaching_class:
            return False

        teaching_class.is_deleted = 1
        await db.commit()
        return True
