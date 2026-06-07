from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.courseDao import CourseDAO
from app.dao.teacherDao import TeacherDAO
from app.dao.teachingClassDao import TeachingClassDAO
from app.dao.classScheduleDao import ClassScheduleDAO

"""
课程服务类，主要职责包括：
1. 创建课程
2. 根据ID查询课程
3. 根据教师ID查询课程列表
4. 查询所有课程
5. 更新课程信息
6. 更新课程状态
7. 删除课程
"""
class CourseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_course(
        self,
        course_code: str,
        course_name: str,
        credit: float,
        teacher_id: int,
        description: str | None = None,
    ):
        teacher = await TeacherDAO.get_by_id(self.db, teacher_id)
        if not teacher:
            raise ValueError("Teacher not found")

        existing = await CourseDAO.get_by_code(self.db, course_code)
        if existing:
            raise ValueError("Course code already exists")

        if credit <= 0:
            raise ValueError("Credit must be greater than 0")

        course = await CourseDAO.create_course(
            self.db,
            course_code=course_code,
            course_name=course_name,
            credit=credit,
            created_by_teacher_id=teacher_id,
            description=description,
        )
        return course

    async def get_course(self, course_id: int):
        course = await CourseDAO.get_by_id(self.db, course_id)
        if not course:
            raise ValueError("Course not found")
        return course

    async def get_teacher_courses(self, teacher_id: int):
        teacher = await TeacherDAO.get_by_id(self.db, teacher_id)
        if not teacher:
            raise ValueError("Teacher not found")

        return await CourseDAO.get_by_teacher(self.db, teacher_id)

    async def get_all_courses(self):
        return await CourseDAO.get_all(self.db)

    async def update_course(self, course_id: int, **kwargs):
        credit = kwargs.get("credit")
        if credit is not None and credit <= 0:
            raise ValueError("Credit must be greater than 0")

        status = kwargs.get("status")
        if status is not None and status not in ["draft", "active", "closed"]:
            raise ValueError("Invalid status")

        course = await CourseDAO.update_course(self.db, course_id, **kwargs)
        if not course:
            raise ValueError("Course not found")
        return course

    async def update_course_status(self, course_id: int, status: str):
        if status not in ["draft", "active", "closed"]:
            raise ValueError("Invalid status")

        course = await CourseDAO.update_status(self.db, course_id, status)
        if not course:
            raise ValueError("Course not found")
        return course

    async def delete_course(self, course_id: int):
        success = await CourseDAO.soft_delete(self.db, course_id)
        if not success:
            raise ValueError("Course not found")
        return {"message": "Course deleted"}
