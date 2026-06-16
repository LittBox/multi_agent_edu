"""学生档案服务。"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.studentDao import StudentDAO
from app.dao.userDao import UserDAO
from app.dao.UserRoleDAO import UserRoleDAO
from app.services._helpers import student_to_dict


class StudentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_student(self, user_id: int, student_no: str, student_name: str,
                             major: str | None = None, grade: int | None = None,
                             class_name: str | None = None) -> dict:
        user = await UserDAO.get_by_id(self.db, user_id)
        if not user:
            raise ValueError("User not found")
        if await StudentDAO.get_by_user_id(self.db, user_id, include_deleted=True):
            raise ValueError("Student profile already exists for this user")
        if await StudentDAO.get_by_student_no(self.db, student_no, include_deleted=True):
            raise ValueError("Student number already exists")
        student = await StudentDAO.create_student(self.db, user_id, student_no, student_name, major, grade, class_name)
        await UserDAO.update_role(self.db, user_id, "student")
        await UserRoleDAO.assign_role_to_user(self.db, user_id, "student")
        return student_to_dict(student)

    async def get_student(self, student_id: int) -> dict:
        student = await StudentDAO.get_by_id(self.db, student_id)
        if not student:
            raise ValueError("Student not found")
        return student_to_dict(student)

    async def get_student_by_user(self, user_id: int) -> dict:
        student = await StudentDAO.get_by_user_id(self.db, user_id)
        if not student:
            raise ValueError("Student not found for this user")
        return student_to_dict(student)

    async def list_students(self, major: str | None = None, grade: int | None = None,
                            class_name: str | None = None) -> list[dict]:
        rows = await StudentDAO.get_all(self.db, major=major, grade=grade, class_name=class_name)
        return [student_to_dict(item) for item in rows]

    async def update_student(self, student_id: int, **kwargs) -> dict:
        allowed = {"student_no", "student_name", "major", "grade", "class_name"}
        data = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        if "student_no" in data:
            existing = await StudentDAO.get_by_student_no(self.db, data["student_no"], include_deleted=True)
            if existing and existing.student_id != student_id:
                raise ValueError("Student number already exists")
        student = await StudentDAO.update_student(self.db, student_id, **data)
        if not student:
            raise ValueError("Student not found")
        return student_to_dict(student)

    async def delete_student(self, student_id: int) -> bool:
        ok = await StudentDAO.soft_delete(self.db, student_id)
        if not ok:
            raise ValueError("Student not found")
        return ok
