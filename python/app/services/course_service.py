"""课程服务。"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.courseDao import CourseDAO
from app.dao.teacherDao import TeacherDAO
from app.dao.teachingClassDao import TeachingClassDAO
from app.services._helpers import course_to_dict, teaching_class_to_dict


class CourseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_course(self, course_code: str, course_name: str, credit: float,
                            teacher_id: int | None = None,
                            created_by_teacher_id: int | None = None,
                            description: str | None = None,
                            status: str = "active") -> dict:
        creator_id = created_by_teacher_id or teacher_id
        if creator_id is None:
            raise ValueError("Teacher id is required")
        if credit <= 0:
            raise ValueError("Credit must be greater than 0")
        if status not in {"draft", "active", "closed"}:
            raise ValueError("Invalid status")
        teacher = await TeacherDAO.get_by_id(self.db, creator_id)
        if not teacher:
            raise ValueError("Teacher not found")
        existing = await CourseDAO.get_by_code(self.db, course_code, include_deleted=True)
        if existing and existing.is_deleted == 0:
            raise ValueError("Course code already exists")
        course = await CourseDAO.create_course(self.db, course_code, course_name, credit,
                                               creator_id, description, status)
        return course_to_dict(course, teacher_name=teacher.teacher_name)

    async def get_course(self, course_id: int) -> dict:
        course = await CourseDAO.get_by_id(self.db, course_id)
        if not course:
            raise ValueError("Course not found")
        teacher = await TeacherDAO.get_by_id(self.db, course.created_by_teacher_id)
        return course_to_dict(course, teacher_name=teacher.teacher_name if teacher else None)

    async def get_teacher_courses(self, teacher_id: int, status: str | None = None) -> list[dict]:
        teacher = await TeacherDAO.get_by_id(self.db, teacher_id)
        if not teacher:
            raise ValueError("Teacher not found")
        rows = await CourseDAO.get_by_teacher(self.db, teacher_id, status=status)
        return [course_to_dict(item, teacher_name=teacher.teacher_name) for item in rows]

    async def get_all_courses(self, status: str | None = None, q: str | None = None) -> list[dict]:
        rows = await CourseDAO.get_all(self.db, status=status)
        if q:
            keyword = q.strip().lower()
            rows = [c for c in rows if keyword in c.course_name.lower() or keyword in c.course_code.lower()]
        result = []
        for course in rows:
            teacher = await TeacherDAO.get_by_id(self.db, course.created_by_teacher_id)
            result.append(course_to_dict(course, teacher_name=teacher.teacher_name if teacher else None))
        return result

    async def update_course(self, course_id: int, **kwargs) -> dict:
        allowed = {"course_code", "course_name", "credit", "description", "created_by_teacher_id", "status"}
        data = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        if "credit" in data and data["credit"] <= 0:
            raise ValueError("Credit must be greater than 0")
        if "status" in data and data["status"] not in {"draft", "active", "closed"}:
            raise ValueError("Invalid status")
        if "created_by_teacher_id" in data and not await TeacherDAO.get_by_id(self.db, data["created_by_teacher_id"]):
            raise ValueError("Teacher not found")
        course = await CourseDAO.update_course(self.db, course_id, **data)
        if not course:
            raise ValueError("Course not found")
        teacher = await TeacherDAO.get_by_id(self.db, course.created_by_teacher_id)
        return course_to_dict(course, teacher_name=teacher.teacher_name if teacher else None)

    async def update_course_status(self, course_id: int, status: str) -> dict:
        if status not in {"draft", "active", "closed"}:
            raise ValueError("Invalid status")
        course = await CourseDAO.update_status(self.db, course_id, status)
        if not course:
            raise ValueError("Course not found")
        return course_to_dict(course)

    async def delete_course(self, course_id: int) -> bool:
        ok = await CourseDAO.soft_delete(self.db, course_id)
        if not ok:
            raise ValueError("Course not found")
        return ok

    async def get_course_classes(self, course_id: int) -> list[dict]:
        course = await CourseDAO.get_by_id(self.db, course_id)
        if not course:
            raise ValueError("Course not found")
        rows = await TeachingClassDAO.get_by_course(self.db, course_id)
        result = []
        for tc in rows:
            teacher = await TeacherDAO.get_by_id(self.db, tc.teacher_id)
            result.append(teaching_class_to_dict(tc, course=course, teacher=teacher))
        return result
