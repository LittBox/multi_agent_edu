from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.task import TaskBank, TaskRelease, TaskSubmission

"""
作业 DAO。
包含 TaskBankDAO、TaskReleaseDAO、TaskSubmissionDAO。
对应 task_bank、task_releases、task_submissions 三张表。
"""

class TaskBankDAO:
    @staticmethod
    async def create_task(db: AsyncSession, course_id: int, teacher_id: int,
                          task_content: str, task_type: str = "homework") -> TaskBank:
        task = TaskBank(course_id=course_id, teacher_id=teacher_id, task_type=task_type, task_content=task_content)
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def get_by_id(db: AsyncSession, task_id: int, include_deleted: bool = False) -> TaskBank | None:
        conditions = [TaskBank.task_id == task_id]
        if not include_deleted:
            conditions.append(TaskBank.is_deleted == 0)
        result = await db.execute(select(TaskBank).where(*conditions))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, course_id: int | None = None, teacher_id: int | None = None,
                      task_type: str | None = None, include_deleted: bool = False) -> list[TaskBank]:
        conditions = []
        if course_id is not None:
            conditions.append(TaskBank.course_id == course_id)
        if teacher_id is not None:
            conditions.append(TaskBank.teacher_id == teacher_id)
        if task_type is not None:
            conditions.append(TaskBank.task_type == task_type)
        if not include_deleted:
            conditions.append(TaskBank.is_deleted == 0)
        stmt = select(TaskBank)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await db.execute(stmt.order_by(TaskBank.created_at.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_task(db: AsyncSession, task_id: int, **kwargs) -> TaskBank | None:
        task = await TaskBankDAO.get_by_id(db, task_id, include_deleted=True)
        if not task:
            return None
        for key in ("course_id", "teacher_id", "task_type", "task_content", "is_deleted"):
            if key in kwargs and kwargs[key] is not None:
                setattr(task, key, kwargs[key])
        task.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def soft_delete(db: AsyncSession, task_id: int) -> bool:
        task = await TaskBankDAO.get_by_id(db, task_id)
        if not task:
            return False
        task.is_deleted = 1
        task.updated_at = datetime.now(UTC)
        await db.commit()
        return True


class TaskReleaseDAO:
    @staticmethod
    async def create_release(db: AsyncSession, task_id: int, publish_time: datetime | None = None,
                             deadline: datetime | None = None) -> TaskRelease:
        data = {"task_id": task_id}
        if publish_time is not None:
            data["publish_time"] = publish_time
        if deadline is not None:
            data["deadline"] = deadline
        release = TaskRelease(**data)
        db.add(release)
        await db.commit()
        await db.refresh(release)
        return release

    @staticmethod
    async def get_by_id(db: AsyncSession, task_publish_id: int,
                        include_deleted: bool = False) -> TaskRelease | None:
        conditions = [TaskRelease.task_publish_id == task_publish_id]
        if not include_deleted:
            conditions.append(TaskRelease.is_deleted == 0)
        result = await db.execute(select(TaskRelease).where(*conditions))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, task_id: int | None = None,
                      include_deleted: bool = False) -> list[TaskRelease]:
        conditions = []
        if task_id is not None:
            conditions.append(TaskRelease.task_id == task_id)
        if not include_deleted:
            conditions.append(TaskRelease.is_deleted == 0)
        stmt = select(TaskRelease)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await db.execute(stmt.order_by(TaskRelease.publish_time.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_release(db: AsyncSession, task_publish_id: int, **kwargs) -> TaskRelease | None:
        release = await TaskReleaseDAO.get_by_id(db, task_publish_id, include_deleted=True)
        if not release:
            return None
        for key in ("task_id", "publish_time", "deadline", "is_deleted"):
            if key in kwargs and kwargs[key] is not None:
                setattr(release, key, kwargs[key])
        release.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(release)
        return release

    @staticmethod
    async def soft_delete(db: AsyncSession, task_publish_id: int) -> bool:
        release = await TaskReleaseDAO.get_by_id(db, task_publish_id)
        if not release:
            return False
        release.is_deleted = 1
        release.updated_at = datetime.now(UTC)
        await db.commit()
        return True


class TaskSubmissionDAO:
    @staticmethod
    async def create_submission(db: AsyncSession, task_publish_id: int, student_id: int,
                                answer_content: str, score: float | None = None,
                                comment: str | None = None,
                                submit_time: datetime | None = None) -> TaskSubmission:
        existed = await TaskSubmissionDAO.get_by_release_student(db, task_publish_id, student_id)
        if existed:
            existed.answer_content = answer_content
            if score is not None:
                existed.score = score
            if comment is not None:
                existed.comment = comment
            existed.submit_time = submit_time or datetime.now(UTC)
            existed.updated_at = datetime.now(UTC)
            await db.commit()
            await db.refresh(existed)
            return existed
        data = {"task_publish_id": task_publish_id, "student_id": student_id, "answer_content": answer_content}
        if score is not None:
            data["score"] = score
        if comment is not None:
            data["comment"] = comment
        if submit_time is not None:
            data["submit_time"] = submit_time
        submission = TaskSubmission(**data)
        db.add(submission)
        await db.commit()
        await db.refresh(submission)
        return submission

    @staticmethod
    async def get_by_id(db: AsyncSession, submit_id: int) -> TaskSubmission | None:
        result = await db.execute(select(TaskSubmission).where(TaskSubmission.submit_id == submit_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_release_student(db: AsyncSession, task_publish_id: int, student_id: int) -> TaskSubmission | None:
        result = await db.execute(select(TaskSubmission).where(
            TaskSubmission.task_publish_id == task_publish_id,
            TaskSubmission.student_id == student_id,
        ))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_release(db: AsyncSession, task_publish_id: int) -> list[TaskSubmission]:
        result = await db.execute(select(TaskSubmission).where(TaskSubmission.task_publish_id == task_publish_id).order_by(TaskSubmission.submit_time.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_student(db: AsyncSession, student_id: int) -> list[TaskSubmission]:
        result = await db.execute(select(TaskSubmission).where(TaskSubmission.student_id == student_id).order_by(TaskSubmission.submit_time.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_submission(db: AsyncSession, submit_id: int, **kwargs) -> TaskSubmission | None:
        submission = await TaskSubmissionDAO.get_by_id(db, submit_id)
        if not submission:
            return None
        for key in ("answer_content", "score", "comment"):
            if key in kwargs and kwargs[key] is not None:
                setattr(submission, key, kwargs[key])
        submission.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(submission)
        return submission

    @staticmethod
    async def grade_submission(db: AsyncSession, submit_id: int, score: float,
                               comment: str | None = None) -> TaskSubmission | None:
        return await TaskSubmissionDAO.update_submission(db, submit_id, score=score, comment=comment)

    @staticmethod
    async def delete_submission(db: AsyncSession, submit_id: int) -> bool:
        submission = await TaskSubmissionDAO.get_by_id(db, submit_id)
        if not submission:
            return False
        await db.delete(submission)
        await db.commit()
        return True
