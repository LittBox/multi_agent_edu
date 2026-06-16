from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.exam import Exam, ExamQuestion, ExamSubmit

"""
考试 DAO。
包含 ExamDAO、ExamQuestionDAO、ExamSubmitDAO。
对应 exams、exam_questions、exam_submits 三张表。
"""

class ExamDAO:
    @staticmethod
    async def create_exam(db: AsyncSession, title: str, course_id: int, teacher_id: int,
                          duration_minutes: int = 60, exam_type: str = "quiz",
                          start_time: datetime | None = None, end_time: datetime | None = None,
                          status: str = "draft") -> Exam:
        exam = Exam(title=title, course_id=course_id, teacher_id=teacher_id,
                    duration_minutes=duration_minutes, exam_type=exam_type,
                    start_time=start_time, end_time=end_time, status=status)
        db.add(exam)
        await db.commit()
        await db.refresh(exam)
        return exam

    @staticmethod
    async def get_by_id(db: AsyncSession, exam_id: int, include_deleted: bool = False) -> Exam | None:
        conditions = [Exam.exam_id == exam_id]
        if not include_deleted:
            conditions.append(Exam.is_deleted == 0)
        result = await db.execute(select(Exam).where(*conditions))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, status: str | None = None, include_deleted: bool = False) -> list[Exam]:
        conditions = []
        if status is not None:
            conditions.append(Exam.status == status)
        if not include_deleted:
            conditions.append(Exam.is_deleted == 0)
        stmt = select(Exam)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await db.execute(stmt.order_by(Exam.created_at.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_course(db: AsyncSession, course_id: int, status: str | None = None) -> list[Exam]:
        conditions = [Exam.course_id == course_id, Exam.is_deleted == 0]
        if status is not None:
            conditions.append(Exam.status == status)
        result = await db.execute(select(Exam).where(*conditions).order_by(Exam.created_at.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_teacher(db: AsyncSession, teacher_id: int, status: str | None = None) -> list[Exam]:
        conditions = [Exam.teacher_id == teacher_id, Exam.is_deleted == 0]
        if status is not None:
            conditions.append(Exam.status == status)
        result = await db.execute(select(Exam).where(*conditions).order_by(Exam.created_at.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_exam(db: AsyncSession, exam_id: int, **kwargs) -> Exam | None:
        exam = await ExamDAO.get_by_id(db, exam_id, include_deleted=True)
        if not exam:
            return None
        for key in ("title", "course_id", "teacher_id", "duration_minutes", "exam_type",
                    "start_time", "end_time", "status", "is_deleted"):
            if key in kwargs and kwargs[key] is not None:
                setattr(exam, key, kwargs[key])
        exam.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(exam)
        return exam

    @staticmethod
    async def update_status(db: AsyncSession, exam_id: int, status: str) -> Exam | None:
        return await ExamDAO.update_exam(db, exam_id, status=status)

    @staticmethod
    async def soft_delete(db: AsyncSession, exam_id: int) -> bool:
        exam = await ExamDAO.get_by_id(db, exam_id)
        if not exam:
            return False
        exam.is_deleted = 1
        exam.updated_at = datetime.now(UTC)
        await db.commit()
        return True


class ExamQuestionDAO:
    @staticmethod
    async def add_question(db: AsyncSession, exam_id: int, question_id: int,
                           score: float = 10, sort_order: int = 0) -> ExamQuestion:
        existed = await ExamQuestionDAO.get_by_exam_question(db, exam_id, question_id)
        if existed:
            existed.score = score
            existed.sort_order = sort_order
            await db.commit()
            await db.refresh(existed)
            return existed
        item = ExamQuestion(exam_id=exam_id, question_id=question_id, score=score, sort_order=sort_order)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def get_by_id(db: AsyncSession, exam_question_id: int) -> ExamQuestion | None:
        result = await db.execute(select(ExamQuestion).where(ExamQuestion.exam_question_id == exam_question_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_exam_question(db: AsyncSession, exam_id: int, question_id: int) -> ExamQuestion | None:
        result = await db.execute(select(ExamQuestion).where(
            ExamQuestion.exam_id == exam_id,
            ExamQuestion.question_id == question_id,
        ))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_exam(db: AsyncSession, exam_id: int) -> list[ExamQuestion]:
        result = await db.execute(select(ExamQuestion).where(ExamQuestion.exam_id == exam_id).order_by(ExamQuestion.sort_order.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_exam_question(db: AsyncSession, exam_question_id: int,
                                   score: float | None = None, sort_order: int | None = None) -> ExamQuestion | None:
        item = await ExamQuestionDAO.get_by_id(db, exam_question_id)
        if not item:
            return None
        if score is not None:
            item.score = score
        if sort_order is not None:
            item.sort_order = sort_order
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def remove_question(db: AsyncSession, exam_id: int, question_id: int) -> bool:
        item = await ExamQuestionDAO.get_by_exam_question(db, exam_id, question_id)
        if not item:
            return False
        await db.delete(item)
        await db.commit()
        return True

    @staticmethod
    async def clear_exam_questions(db: AsyncSession, exam_id: int) -> int:
        items = await ExamQuestionDAO.get_by_exam(db, exam_id)
        for item in items:
            await db.delete(item)
        await db.commit()
        return len(items)


class ExamSubmitDAO:
    @staticmethod
    async def create_submit(db: AsyncSession, exam_id: int, student_id: int,
                            answers_json: list | dict | None = None,
                            total_score: float | None = None,
                            teacher_comment: str | None = None,
                            submit_time: datetime | None = None) -> ExamSubmit:
        existed = await ExamSubmitDAO.get_by_exam_student(db, exam_id, student_id)
        if existed:
            if answers_json is not None:
                existed.answers_json = answers_json
            if total_score is not None:
                existed.total_score = total_score
            if teacher_comment is not None:
                existed.teacher_comment = teacher_comment
            existed.submit_time = submit_time or datetime.now(UTC)
            existed.updated_at = datetime.now(UTC)
            await db.commit()
            await db.refresh(existed)
            return existed
        data = {"exam_id": exam_id, "student_id": student_id}
        if answers_json is not None:
            data["answers_json"] = answers_json
        if total_score is not None:
            data["total_score"] = total_score
        if teacher_comment is not None:
            data["teacher_comment"] = teacher_comment
        if submit_time is not None:
            data["submit_time"] = submit_time
        submit = ExamSubmit(**data)
        db.add(submit)
        await db.commit()
        await db.refresh(submit)
        return submit

    @staticmethod
    async def get_by_id(db: AsyncSession, exam_submit_id: int) -> ExamSubmit | None:
        result = await db.execute(select(ExamSubmit).where(ExamSubmit.exam_submit_id == exam_submit_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_exam_student(db: AsyncSession, exam_id: int, student_id: int) -> ExamSubmit | None:
        result = await db.execute(select(ExamSubmit).where(ExamSubmit.exam_id == exam_id, ExamSubmit.student_id == student_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_exam(db: AsyncSession, exam_id: int) -> list[ExamSubmit]:
        result = await db.execute(select(ExamSubmit).where(ExamSubmit.exam_id == exam_id).order_by(ExamSubmit.submit_time.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_student(db: AsyncSession, student_id: int) -> list[ExamSubmit]:
        result = await db.execute(select(ExamSubmit).where(ExamSubmit.student_id == student_id).order_by(ExamSubmit.submit_time.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_submit(db: AsyncSession, exam_submit_id: int, **kwargs) -> ExamSubmit | None:
        submit = await ExamSubmitDAO.get_by_id(db, exam_submit_id)
        if not submit:
            return None
        for key in ("total_score", "teacher_comment", "answers_json"):
            if key in kwargs and kwargs[key] is not None:
                setattr(submit, key, kwargs[key])
        submit.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(submit)
        return submit

    @staticmethod
    async def grade_submit(db: AsyncSession, exam_submit_id: int, total_score: float,
                           teacher_comment: str | None = None) -> ExamSubmit | None:
        return await ExamSubmitDAO.update_submit(db, exam_submit_id, total_score=total_score, teacher_comment=teacher_comment)

    @staticmethod
    async def delete_submit(db: AsyncSession, exam_submit_id: int) -> bool:
        submit = await ExamSubmitDAO.get_by_id(db, exam_submit_id)
        if not submit:
            return False
        await db.delete(submit)
        await db.commit()
        return True
