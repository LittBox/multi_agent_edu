from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.studentDao import StudentDAO
from app.dao.userDao import UserDAO

"""
学生服务类，主要职责包括：
1. 创建学生档案
2. 根据学生ID查询学生信息
3. 根据用户ID查询学生信息
4. 查询所有学生信息
5. 更新学生信息
6. 删除学生档案
"""
class StudentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_student(
        self,
        user_id: int,
        student_no: str,
        student_name: str,
        major: str | None = None,
        grade: int | None = None,
        class_name: str | None = None,
    ):
        user = await UserDAO.get_by_id(self.db, user_id)
        if not user:
            raise ValueError("User not found")

        existing_profile = await StudentDAO.get_by_user_id(self.db, user_id)
        if existing_profile:
            raise ValueError("Student profile already exists for this user")

        existing = await StudentDAO.get_by_student_no(self.db, student_no)
        if existing:
            raise ValueError("Student number already exists")

        student = await StudentDAO.create_student(
            self.db,
            user_id=user_id,
            student_no=student_no,
            student_name=student_name,
            major=major,
            grade=grade,
            class_name=class_name,
        )
        await UserDAO.update_role(self.db, user_id, "student")
        return student

    async def get_student(self, student_id: int):
        student = await StudentDAO.get_by_id(self.db, student_id)
        if not student:
            raise ValueError("Student not found")
        return student

    async def get_student_by_user(self, user_id: int):
        student = await StudentDAO.get_by_user_id(self.db, user_id)
        if not student:
            raise ValueError("Student not found for this user")
        return student

    async def get_all_students(self):
        return await StudentDAO.get_all(self.db)

    async def update_student(self, student_id: int, **kwargs):
        student = await StudentDAO.update_student(self.db, student_id, **kwargs)
        if not student:
            raise ValueError("Student not found")
        return student

    async def delete_student(self, student_id: int):
        success = await StudentDAO.soft_delete(self.db, student_id)
        if not success:
            raise ValueError("Student not found")
        return {"message": "Student deleted"}
