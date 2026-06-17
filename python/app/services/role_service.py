"""角色服务。"""
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.roleDao import RoleDAO
from app.dao.UserRoleDAO import UserRoleDAO
from app.db.models.user import User
from app.db.models.student import Student
from app.core.security import hash_password

class StudentRoleCreatePayload(BaseModel):
    username: str
    email: Optional[str] = None
    password: str

    student_no: Optional[str] = None
    student_name: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[int] = None
    class_name: Optional[str] = None


class StudentRoleUpdatePayload(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

    student_no: Optional[str] = None
    student_name: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[int] = None
    class_name: Optional[str] = None


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def to_dict(role) -> dict:
        return {"role_id": role.role_id, "role_name": role.role_name}

    async def create_role(self, role_name: str) -> dict:
        if await RoleDAO.get_by_name(self.db, role_name):
            raise ValueError("Role already exists")
        return self.to_dict(await RoleDAO.create_role(self.db, role_name))

    async def list_roles(self) -> list[dict]:
        return [self.to_dict(r) for r in await RoleDAO.get_all(self.db)]

    async def update_role(self, role_id: int, role_name: str) -> dict:
        role = await RoleDAO.update_role(self.db, role_id, role_name)
        if not role:
            raise ValueError("Role not found")
        return self.to_dict(role)

    async def delete_role(self, role_id: int) -> bool:
        ok = await RoleDAO.delete_role(self.db, role_id)
        if not ok:
            raise ValueError("Role not found")
        return ok

    async def assign_role_to_user(self, user_id: int, role_name: str) -> dict:
        user_role = await UserRoleDAO.assign_role_to_user(self.db, user_id, role_name)
        return {"id": user_role.id, "user_id": user_role.user_id, "role_id": user_role.role_id}
    
    @staticmethod
    def student_role_to_dict(user: User, student: Optional[Student], role_name: str = "student") -> dict:
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role_name": role_name,

            "student_id": student.student_id if student else None,
            "student_no": student.student_no if student else None,
            "student_name": student.student_name if student else None,
            "major": student.major if student else None,
            "grade": student.grade if student else None,
            "class_name": student.class_name if student else None,
        }

    async def create_student_role_user(self, payload: StudentRoleCreatePayload) -> dict:
            exists = await self.db.execute(
                select(User).where(User.username == payload.username)
            )
            if exists.scalar_one_or_none():
                raise ValueError("Username already exists")

            if payload.email:
                exists_email = await self.db.execute(
                    select(User).where(User.email == payload.email)
                )
                if exists_email.scalar_one_or_none():
                    raise ValueError("Email already exists")

            user = User(
                username=payload.username,
                email=payload.email,
                password_hash=hash_password(payload.password),
            )
            self.db.add(user)
            await self.db.flush()

            await UserRoleDAO.assign_role_to_user(self.db, user.user_id, "student")

            student = Student(
                user_id=user.user_id,
                student_no=payload.student_no,
                student_name=payload.student_name,
                major=payload.major,
                grade=payload.grade,
                class_name=payload.class_name,
            )
            self.db.add(student)

            await self.db.commit()
            await self.db.refresh(user)
            await self.db.refresh(student)

            return self.student_role_to_dict(user, student)

    async def update_student_role_user(
        self,
        user_id: int,
        payload: StudentRoleUpdatePayload,
    ) -> dict:
        user_result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        student_result = await self.db.execute(
            select(Student).where(Student.user_id == user_id)
        )
        student = student_result.scalar_one_or_none()

        if not student:
            raise ValueError("Student info not found")

        update_data = payload.model_dump(exclude_unset=True)

        user_fields = {"username", "email", "password"}
        student_fields = {
                    "student_no",
                    "student_name",
                    "major",
                    "grade",
                    "class_name",
                }

        for field, value in update_data.items():
            if field in user_fields:
                if field == "password":
                    if value:
                        user.password_hash = hash_password(value)
                else:
                    setattr(user, field, value)

            if field in student_fields:
                setattr(student, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        await self.db.refresh(student)

        return self.student_role_to_dict(user, student)
    
    async def get_my_student_info(self, user_id: int) -> dict:
        user_result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        student_result = await self.db.execute(
            select(Student).where(Student.user_id == user_id)
        )
        student = student_result.scalar_one_or_none()

        return self.student_role_to_dict(user, student)


    async def update_my_student_info(
        self,
        user_id: int,
        payload: StudentRoleUpdatePayload,
    ) -> dict:
        user_result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        student_result = await self.db.execute(
            select(Student).where(Student.user_id == user_id)
        )
        student = student_result.scalar_one_or_none()

        update_data = payload.model_dump(exclude_unset=True)

        user_fields = {"username", "email", "password"}
        student_fields = {
            "student_no",
            "student_name",
            "major",
            "grade",
            "class_name",
        }

        for field, value in update_data.items():
            if field in user_fields:
                if field == "password":
                    if value:
                        user.password_hash = hash_password(value)
                else:
                    setattr(user, field, value)

        student_data = {
            field: value
            for field, value in update_data.items()
            if field in student_fields
        }

        if student is None:
            student = Student(
                user_id=user_id,
                student_no=student_data.get("student_no"),
                student_name=student_data.get("student_name"),
                major=student_data.get("major"),
                grade=student_data.get("grade"),
                class_name=student_data.get("class_name"),
            )
            self.db.add(student)
        else:
            for field, value in student_data.items():
                setattr(student, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        await self.db.refresh(student)

        return self.student_role_to_dict(user, student)