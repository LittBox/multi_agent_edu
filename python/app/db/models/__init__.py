"""
模型层统一导出文件。

建议在 app/models/__init__.py 中导入所有模型，确保 SQLAlchemy Base.metadata
能够收集到全部表结构，尤其是新增的考试、作业、权限关联模型。
"""

from app.db.models.answer_record import AnswerRecord
from app.db.models.course import Course
from app.db.models.course_enrollment import CourseEnrollment
from app.db.models.exam import Exam, ExamQuestion, ExamSubmit
from app.db.models.knowledge_point import KnowledgePoint
from app.db.models.learner_state import LearnerState
from app.db.models.menu import Menu
from app.db.models.permission import Permission, PermissionMenu, RolePermission
from app.db.models.question import Question
from app.db.models.review_schedule import ReviewSchedule
from app.db.models.role import Role
from app.db.models.role_menu import RoleMenu
from app.db.models.student import Student
from app.db.models.task import TaskBank, TaskRelease, TaskSubmission
from app.db.models.teacher import Teacher
from app.db.models.teaching_class import TeachingClass
from app.db.models.user import User
from app.db.models.user_role import UserRole

__all__ = [
    "AnswerRecord",
    "Course",
    "CourseEnrollment",
    "Exam",
    "ExamQuestion",
    "ExamSubmit",
    "KnowledgePoint",
    "LearnerState",
    "Menu",
    "Permission",
    "PermissionMenu",
    "Question",
    "ReviewSchedule",
    "Role",
    "RoleMenu",
    "RolePermission",
    "Student",
    "TaskBank",
    "TaskRelease",
    "TaskSubmission",
    "Teacher",
    "TeachingClass",
    "User",
    "UserRole",
]
