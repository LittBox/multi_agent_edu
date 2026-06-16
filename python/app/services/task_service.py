"""作业服务。

对应前端 TaskView：
- list_bank：教师/管理员查看作业题库
- create_bank：教师创建作业题库条目
- release：发布作业
- list_releases：学生上方已发布作业卡片
- submit：学生提交作业答案
- my_submissions：学生下方我的作业进度/提交记录
"""
from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.courseDao import CourseDAO
from app.dao.studentDao import StudentDAO
from app.dao.taskDao import TaskBankDAO, TaskReleaseDAO, TaskSubmissionDAO
from app.dao.teacherDao import TeacherDAO
from app.services._helpers import task_bank_to_dict, task_release_to_dict, task_submission_to_dict


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_bank(self, course_id: int, teacher_id: int,
                          task_type: str = "homework", task_content: str = "") -> dict:
        if not task_content.strip():
            raise ValueError("Task content is required")
        course = await CourseDAO.get_by_id(self.db, course_id)
        if not course:
            raise ValueError("Course not found")
        teacher = await TeacherDAO.get_by_id(self.db, teacher_id)
        if not teacher:
            raise ValueError("Teacher not found")
        task = await TaskBankDAO.create_task(self.db, course_id, teacher_id, task_content.strip(), task_type)
        return task_bank_to_dict(task, course=course, teacher=teacher)

    async def create_bank_by_user(self, user_id: int, course_id: int,
                                  task_type: str = "homework", task_content: str = "") -> dict:
        teacher = await TeacherDAO.get_by_user_id(self.db, user_id)
        if not teacher:
            raise ValueError("Teacher profile not found for current user")
        return await self.create_bank(course_id, teacher.teacher_id, task_type, task_content)

    async def list_bank(self, course_id: int | None = None,
                        teacher_id: int | None = None) -> list[dict]:
        rows = await TaskBankDAO.get_all(self.db, course_id=course_id, teacher_id=teacher_id)
        result = []
        for task in rows:
            course = await CourseDAO.get_by_id(self.db, task.course_id)
            teacher = await TeacherDAO.get_by_id(self.db, task.teacher_id)
            result.append(task_bank_to_dict(task, course=course, teacher=teacher))
        return result

    async def update_bank(self, task_id: int, **kwargs) -> dict:
        allowed = {"course_id", "teacher_id", "task_type", "task_content"}
        data = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        if "course_id" in data and not await CourseDAO.get_by_id(self.db, data["course_id"]):
            raise ValueError("Course not found")
        if "teacher_id" in data and not await TeacherDAO.get_by_id(self.db, data["teacher_id"]):
            raise ValueError("Teacher not found")
        task = await TaskBankDAO.update_task(self.db, task_id, **data)
        if not task:
            raise ValueError("Task not found")
        course = await CourseDAO.get_by_id(self.db, task.course_id)
        teacher = await TeacherDAO.get_by_id(self.db, task.teacher_id)
        return task_bank_to_dict(task, course=course, teacher=teacher)

    async def delete_bank(self, task_id: int) -> bool:
        ok = await TaskBankDAO.soft_delete(self.db, task_id)
        if not ok:
            raise ValueError("Task not found")
        return ok

    async def release(self, task_id: int, deadline: datetime | None = None,
                      publish_time: datetime | None = None) -> dict:
        task = await TaskBankDAO.get_by_id(self.db, task_id)
        if not task:
            raise ValueError("Task not found")
        release = await TaskReleaseDAO.create_release(self.db, task_id,
                                                      publish_time=publish_time or datetime.now(UTC),
                                                      deadline=deadline)
        course = await CourseDAO.get_by_id(self.db, task.course_id)
        teacher = await TeacherDAO.get_by_id(self.db, task.teacher_id)
        return task_release_to_dict(release, task=task, course=course, teacher=teacher)

    async def list_releases(self, task_id: int | None = None) -> list[dict]:
        rows = await TaskReleaseDAO.get_all(self.db, task_id=task_id)
        result = []
        for release in rows:
            task = await TaskBankDAO.get_by_id(self.db, release.task_id)
            course = await CourseDAO.get_by_id(self.db, task.course_id) if task else None
            teacher = await TeacherDAO.get_by_id(self.db, task.teacher_id) if task else None
            result.append(task_release_to_dict(release, task=task, course=course, teacher=teacher))
        return result

    async def update_release(self, task_publish_id: int, **kwargs) -> dict:
        allowed = {"deadline", "publish_time", "is_deleted"}
        data = {k: v for k, v in kwargs.items() if k in allowed}
        release = await TaskReleaseDAO.update_release(self.db, task_publish_id, **data)
        if not release:
            raise ValueError("Task release not found")
        task = await TaskBankDAO.get_by_id(self.db, release.task_id)
        return task_release_to_dict(release, task=task)

    async def delete_release(self, task_publish_id: int) -> bool:
        ok = await TaskReleaseDAO.soft_delete(self.db, task_publish_id)
        if not ok:
            raise ValueError("Task release not found")
        return ok

    async def submit(self, task_publish_id: int, user_id: int, answer_content: str) -> dict:
        if not answer_content.strip():
            raise ValueError("Answer content is required")
        student = await StudentDAO.get_by_user_id(self.db, user_id)
        if not student:
            raise ValueError("Student profile not found for current user")
        release = await TaskReleaseDAO.get_by_id(self.db, task_publish_id)
        if not release:
            raise ValueError("Task release not found")
        submission = await TaskSubmissionDAO.create_submission(self.db, task_publish_id, student.student_id,
                                                               answer_content.strip(), submit_time=datetime.now(UTC))
        task = await TaskBankDAO.get_by_id(self.db, release.task_id)
        return task_submission_to_dict(submission, release=release, task=task)

    async def my_submissions(self, user_id: int) -> list[dict]:
        student = await StudentDAO.get_by_user_id(self.db, user_id)
        if not student:
            raise ValueError("Student profile not found for current user")
        rows = await TaskSubmissionDAO.get_by_student(self.db, student.student_id)
        result = []
        for sub in rows:
            release = await TaskReleaseDAO.get_by_id(self.db, sub.task_publish_id)
            task = await TaskBankDAO.get_by_id(self.db, release.task_id) if release else None
            result.append(task_submission_to_dict(sub, release=release, task=task))
        return result

    async def grade_submission(self, submit_id: int, score: float,
                               comment: str | None = None) -> dict:
        if score < 0:
            raise ValueError("Score must be non-negative")
        sub = await TaskSubmissionDAO.grade_submission(self.db, submit_id, score, comment)
        if not sub:
            raise ValueError("Task submission not found")
        release = await TaskReleaseDAO.get_by_id(self.db, sub.task_publish_id)
        task = await TaskBankDAO.get_by_id(self.db, release.task_id) if release else None
        return task_submission_to_dict(sub, release=release, task=task)
