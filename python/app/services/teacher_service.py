"""教师档案服务。"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.teacherDao import TeacherDAO
from app.dao.userDao import UserDAO
from app.dao.UserRoleDAO import UserRoleDAO
from app.services._helpers import teacher_to_dict


class TeacherService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_teacher(self, user_id: int, teacher_no: str, teacher_name: str,
                             department: str | None = None, title: str | None = None) -> dict:
        user = await UserDAO.get_by_id(self.db, user_id)
        if not user:
            raise ValueError("User not found")
        if await TeacherDAO.get_by_user_id(self.db, user_id, include_deleted=True):
            raise ValueError("Teacher profile already exists for this user")
        if await TeacherDAO.get_by_teacher_no(self.db, teacher_no, include_deleted=True):
            raise ValueError("Teacher number already exists")
        teacher = await TeacherDAO.create_teacher(self.db, user_id, teacher_no, teacher_name, department, title)
        await UserDAO.update_role(self.db, user_id, "teacher")
        await UserRoleDAO.assign_role_to_user(self.db, user_id, "teacher")
        return teacher_to_dict(teacher)

    async def get_teacher(self, teacher_id: int) -> dict:
        teacher = await TeacherDAO.get_by_id(self.db, teacher_id)
        if not teacher:
            raise ValueError("Teacher not found")
        return teacher_to_dict(teacher)

    async def get_teacher_by_user(self, user_id: int) -> dict:
        teacher = await TeacherDAO.get_by_user_id(self.db, user_id)
        if not teacher:
            raise ValueError("Teacher not found for this user")
        return teacher_to_dict(teacher)

    async def list_teachers(self, department: str | None = None, title: str | None = None) -> list[dict]:
        rows = await TeacherDAO.get_all(self.db, department=department, title=title)
        return [teacher_to_dict(item) for item in rows]

    async def update_teacher(self, teacher_id: int, **kwargs) -> dict:
        allowed = {"teacher_no", "teacher_name", "department", "title"}
        data = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        if "teacher_no" in data:
            existing = await TeacherDAO.get_by_teacher_no(self.db, data["teacher_no"], include_deleted=True)
            if existing and existing.teacher_id != teacher_id:
                raise ValueError("Teacher number already exists")
        teacher = await TeacherDAO.update_teacher(self.db, teacher_id, **data)
        if not teacher:
            raise ValueError("Teacher not found")
        return teacher_to_dict(teacher)

    async def delete_teacher(self, teacher_id: int) -> bool:
        ok = await TeacherDAO.soft_delete(self.db, teacher_id)
        if not ok:
            raise ValueError("Teacher not found")
        return ok
