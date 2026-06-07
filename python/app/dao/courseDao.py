from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.course import Course


"""
课程对象数据访问对象（DAO，Data Access Object），提供对课程表的增删改查操作，包括创建课程、根据ID查询课程、根据课程代码查询课程、根据教师ID查询课程列表、查询所有课程、更新课程信息、更新课程状态、删除课程等功能。
课程DAO的主要职责包括：
1. 创建课程：根据课程代码、课程名称、学分、课程描述、创建者教师ID等信息创建新的课程记录，并检查课程代码的唯一性。
2. 根据ID查询课程：根据课程ID查询课程的详细信息，包括课程代码、课程名称、学分、课程描述、创建者教师ID、课程状态等信息。
3. 根据课程代码查询课程：根据课程代码查询课程的详细信息，包括课程ID、课程名称、学分、课程描述、创建者教师ID、课程状态等信息。
4. 根据教师ID查询课程列表：根据教师ID查询该教师创建的所有课程，并返回一个列表，包含每条记录的详细信息。
5. 查询所有课程：查询所有课程记录，并返回一个列表，包含每条记录的详细信息。
6. 更新课程信息：根据课程ID更新课程的相关信息，例如修改课程名称、调整学分、变更课程描述等，并检查更新后的信息是否合理。
7. 更新课程状态：根据课程ID更新课程的状态，例如将课程状态从“active”变更为“inactive”，以控制课程的可用性。
8. 删除课程：根据课程ID删除课程记录，实际操作为软删除，即将记录的状态标记为“deleted”，以保留历史数据。  
"""
class CourseDAO:

    @staticmethod
    async def create_course(
        db: AsyncSession,
        course_code: str,
        course_name: str,
        credit: float,
        created_by_teacher_id: int,
        description: str | None = None,
        status: str = "active",
    ) -> Course:
        course = Course(
            course_code=course_code,
            course_name=course_name,
            credit=credit,
            created_by_teacher_id=created_by_teacher_id,
            description=description,
            status=status,
        )
        db.add(course)
        await db.commit()
        await db.refresh(course)
        return course

    @staticmethod
    async def get_by_id(db: AsyncSession, course_id: int) -> Course | None:
        result = await db.execute(
            select(Course).where(
                Course.course_id == course_id,
                Course.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_code(db: AsyncSession, course_code: str) -> Course | None:
        result = await db.execute(
            select(Course).where(
                Course.course_code == course_code,
                Course.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_teacher(db: AsyncSession, teacher_id: int):
        result = await db.execute(
            select(Course).where(
                Course.created_by_teacher_id == teacher_id,
                Course.is_deleted == 0
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(
            select(Course).where(Course.is_deleted == 0)
        )
        return result.scalars().all()

    @staticmethod
    async def update_course(
        db: AsyncSession,
        course_id: int,
        **kwargs
    ) -> Course | None:
        course = await CourseDAO.get_by_id(db, course_id)
        if not course:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(course, key) and key != "created_by_teacher_id":
                setattr(course, key, value)

        await db.commit()
        await db.refresh(course)
        return course

    @staticmethod
    async def update_status(db: AsyncSession, course_id: int, status: str) -> Course | None:
        course = await CourseDAO.get_by_id(db, course_id)
        if not course:
            return None

        course.status = status
        await db.commit()
        await db.refresh(course)
        return course

    @staticmethod
    async def soft_delete(db: AsyncSession, course_id: int) -> bool:
        course = await CourseDAO.get_by_id(db, course_id)
        if not course:
            return False

        course.is_deleted = 1
        await db.commit()
        return True
