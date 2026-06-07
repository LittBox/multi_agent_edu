from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.teacherDao import TeacherDAO
from app.dao.userDao import UserDAO

"""
教师服务类，提供与教师相关的业务逻辑处理，包括创建教师档案、查询教师信息、更新教师信息、删除教师档案等功能。
教师服务类的主要职责包括：
1. 创建教师档案：根据用户ID、教师编号、教师姓名、所属院系、职称等信息创建新的教师档案，并检查用户是否存在以及教师编号是否   唯一。
2. 查询教师信息：根据教师ID查询教师的详细信息，包括教师编号、姓名、所属院系、职称、联系方式等信息。
3. 更新教师信息：根据教师ID更新教师的相关信息，例如修改教师姓名、调整所属院系、变更职称等，并检查更新后的信息是否合理。
4. 删除教师档案：根据教师ID删除教师档案，实际操作为软删除，即将教师档案的状态标记为“deleted”，以保留历史数据。
"""
class TeacherService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    """
    创建教师档案
    1. 验证用户的存在性。
    2. 验证教师档案的唯一性。
    3. 创建教师档案，并更新用户的联系方式和角色信息。
    """
    async def create_teacher(
        self,
        user_id: int,
        teacher_no: str,
        teacher_name: str,
        department: str | None = None,
        title: str | None = None,
        phone: str | None = None,
        email: str | None = None,
    ):
        user = await UserDAO.get_by_id(self.db, user_id)
        if not user:
            raise ValueError("User not found")

        existing_profile = await TeacherDAO.get_by_user_id(self.db, user_id)
        if existing_profile:
            raise ValueError("Teacher profile already exists for this user")

        existing = await TeacherDAO.get_by_teacher_no(self.db, teacher_no)
        if existing:
            raise ValueError("Teacher number already exists")

        teacher = await TeacherDAO.create_teacher(
            self.db,
            user_id=user_id,
            teacher_no=teacher_no,
            teacher_name=teacher_name,
            department=department,
            title=title,
        )
        if phone is not None or email is not None:
            await UserDAO.update_contact_info(self.db, user_id, email=email, phone=phone)
        await UserDAO.update_role(self.db, user_id, "teacher")
        return teacher


    """
    根据教师ID查询教师信息
    1. 验证教师的存在性。
    2. 返回教师的详细信息，包括教师编号、姓名、所属院系、职称、联系方式等信息。
    """
    async def get_teacher(self, teacher_id: int):
        teacher = await TeacherDAO.get_by_id(self.db, teacher_id)
        if not teacher:
            raise ValueError("Teacher not found")
        return teacher

    """
    根据用户ID查询教师信息
    1. 验证教师的存在性。
    2. 返回教师的详细信息，包括教师编号、姓名、所属院系、职称、联系方式等信息。
    """
    async def get_teacher_by_user(self, user_id: int):
        teacher = await TeacherDAO.get_by_user_id(self.db, user_id)
        if not teacher:
            raise ValueError("Teacher not found for this user")
        return teacher

    """
    查询所有教师信息
    1. 返回所有教师的详细信息。
    """
    async def get_all_teachers(self):
        return await TeacherDAO.get_all(self.db)


    """
    更新教师信息
    1. 验证教师的存在性。
    2. 更新教师的相关信息。
    """
    async def update_teacher(self, teacher_id: int, **kwargs):
        contact_email = kwargs.pop("email", None)
        contact_phone = kwargs.pop("phone", None)

        teacher = await TeacherDAO.get_by_id(self.db, teacher_id)
        if not teacher:
            raise ValueError("Teacher not found")

        if contact_email is not None or contact_phone is not None:
            await UserDAO.update_contact_info(
                self.db,
                teacher.user_id,
                email=contact_email,
                phone=contact_phone,
            )

        teacher = await TeacherDAO.update_teacher(self.db, teacher_id, **kwargs)
        if not teacher:
            raise ValueError("Teacher not found")
        return teacher

    """
    删除教师档案
    1. 验证教师的存在性。
    2. 执行软删除操作。
    """
    async def delete_teacher(self, teacher_id: int):
        success = await TeacherDAO.soft_delete(self.db, teacher_id)
        if not success:
            raise ValueError("Teacher not found")
        return {"message": "Teacher deleted"}
