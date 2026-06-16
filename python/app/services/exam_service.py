"""考试服务。

对应前端 ExamView：
- list_exams：展示已发布考试卡片
- create_exam：教师/管理员创建并发布考试
- add_question / remove_question：组卷
- start_exam：学生进入考试，返回试卷详情
- submit_exam：学生提交答案，自动计算客观题分数
- my_submissions：学生查看考试记录
"""
from datetime import datetime, UTC
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.courseDao import CourseDAO
from app.dao.examDao import ExamDAO, ExamQuestionDAO, ExamSubmitDAO
from app.dao.questionDao import QuestionDAO
from app.dao.studentDao import StudentDAO
from app.dao.teacherDao import TeacherDAO
from app.services._helpers import exam_to_dict, exam_question_to_dict, exam_submit_to_dict


class ExamService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_exam(self, title: str, course_id: int, teacher_id: int,
                          duration_minutes: int = 60, exam_type: str = "quiz",
                          start_time: datetime | None = None, end_time: datetime | None = None,
                          status: str = "draft") -> dict:
        if not title.strip():
            raise ValueError("Exam title is required")
        if duration_minutes <= 0:
            raise ValueError("Duration minutes must be positive")
        if status not in {"draft", "published", "closed", "finished", "cancelled", "active", "ongoing"}:
            raise ValueError("Invalid exam status")
        course = await CourseDAO.get_by_id(self.db, course_id)
        if not course:
            raise ValueError("Course not found")
        teacher = await TeacherDAO.get_by_id(self.db, teacher_id)
        if not teacher:
            raise ValueError("Teacher not found")
        exam = await ExamDAO.create_exam(self.db, title.strip(), course_id, teacher_id,
                                         duration_minutes=duration_minutes, exam_type=exam_type,
                                         start_time=start_time, end_time=end_time, status=status)
        return exam_to_dict(exam, course=course, teacher=teacher)

    async def create_exam_by_user(self, user_id: int, title: str, course_id: int,
                                  duration_minutes: int = 60, exam_type: str = "quiz",
                                  start_time: datetime | None = None, end_time: datetime | None = None,
                                  status: str = "published") -> dict:
        teacher = await TeacherDAO.get_by_user_id(self.db, user_id)
        if not teacher:
            raise ValueError("Teacher profile not found for current user")
        return await self.create_exam(title, course_id, teacher.teacher_id, duration_minutes,
                                      exam_type, start_time, end_time, status)

    async def list_exams(self, status: str | None = None) -> list[dict]:
        rows = await ExamDAO.get_all(self.db, status=status)
        result = []
        for exam in rows:
            course = await CourseDAO.get_by_id(self.db, exam.course_id)
            teacher = await TeacherDAO.get_by_id(self.db, exam.teacher_id)
            result.append(exam_to_dict(exam, course=course, teacher=teacher))
        return result

    async def get_exam(self, exam_id: int, include_questions: bool = False,
                       include_answer: bool = False) -> dict:
        exam = await ExamDAO.get_by_id(self.db, exam_id)
        if not exam:
            raise ValueError("Exam not found")
        course = await CourseDAO.get_by_id(self.db, exam.course_id)
        teacher = await TeacherDAO.get_by_id(self.db, exam.teacher_id)
        data = exam_to_dict(exam, course=course, teacher=teacher)
        if include_questions:
            data["questions"] = await self.list_exam_questions(exam_id, include_answer=include_answer)
        return data

    async def update_exam(self, exam_id: int, **kwargs) -> dict:
        allowed = {"title", "course_id", "teacher_id", "duration_minutes", "exam_type", "start_time", "end_time", "status"}
        data = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        if data.get("duration_minutes") is not None and data["duration_minutes"] <= 0:
            raise ValueError("Duration minutes must be positive")
        if data.get("course_id") is not None and not await CourseDAO.get_by_id(self.db, data["course_id"]):
            raise ValueError("Course not found")
        if data.get("teacher_id") is not None and not await TeacherDAO.get_by_id(self.db, data["teacher_id"]):
            raise ValueError("Teacher not found")
        exam = await ExamDAO.update_exam(self.db, exam_id, **data)
        if not exam:
            raise ValueError("Exam not found")
        return await self.get_exam(exam.exam_id)

    async def delete_exam(self, exam_id: int) -> bool:
        ok = await ExamDAO.soft_delete(self.db, exam_id)
        if not ok:
            raise ValueError("Exam not found")
        return ok

    async def add_question(self, exam_id: int, question_id: int,
                           score: float = 10, sort_order: int = 0) -> dict:
        if score <= 0:
            raise ValueError("Question score must be positive")
        if not await ExamDAO.get_by_id(self.db, exam_id):
            raise ValueError("Exam not found")
        if not await QuestionDAO.get_by_id(self.db, question_id):
            raise ValueError("Question not found")
        eq = await ExamQuestionDAO.add_question(self.db, exam_id, question_id, score, sort_order)
        question = await QuestionDAO.get_by_id(self.db, question_id)
        return exam_question_to_dict(eq, question=question, include_answer=True)

    async def list_exam_questions(self, exam_id: int, include_answer: bool = False) -> list[dict]:
        rows = await ExamQuestionDAO.get_by_exam(self.db, exam_id)
        result = []
        for eq in rows:
            q = await QuestionDAO.get_by_id(self.db, eq.question_id)
            result.append(exam_question_to_dict(eq, question=q, include_answer=include_answer))
        return result

    async def remove_question(self, exam_id: int, question_id: int) -> bool:
        ok = await ExamQuestionDAO.remove_question(self.db, exam_id, question_id)
        if not ok:
            raise ValueError("Exam question not found")
        return ok

    async def start_exam(self, exam_id: int, user_id: int | None = None) -> dict:
        exam = await ExamDAO.get_by_id(self.db, exam_id)
        if not exam:
            raise ValueError("Exam not found")
        if exam.status not in {"published", "active", "ongoing"}:
            raise ValueError("Exam is not available")
        return await self.get_exam(exam_id, include_questions=True, include_answer=False)

    @staticmethod
    def _normalize_answers(answers: dict[str, Any] | list[dict]) -> dict[str, str]:
        if isinstance(answers, dict):
            return {str(k): str(v).strip() for k, v in answers.items()}
        result = {}
        for item in answers or []:
            qid = item.get("question_id")
            answer = item.get("answer")
            if qid is not None:
                result[str(qid)] = "" if answer is None else str(answer).strip()
        return result

    async def submit_exam(self, exam_id: int, user_id: int, answers: dict[str, Any] | list[dict]) -> dict:
        student = await StudentDAO.get_by_user_id(self.db, user_id)
        if not student:
            raise ValueError("Student profile not found for current user")
        exam = await ExamDAO.get_by_id(self.db, exam_id)
        if not exam:
            raise ValueError("Exam not found")
        normalized = self._normalize_answers(answers)
        exam_questions = await ExamQuestionDAO.get_by_exam(self.db, exam_id)
        total_score = 0.0
        answer_items = []
        for eq in exam_questions:
            q = await QuestionDAO.get_by_id(self.db, eq.question_id)
            user_answer = normalized.get(str(eq.question_id), "")
            correct = bool(q and user_answer.strip().upper() == q.answer.strip().upper())
            if correct:
                total_score += float(eq.score)
            answer_items.append({
                "question_id": eq.question_id,
                "answer": user_answer,
                "is_correct": correct,
                "score": float(eq.score) if correct else 0.0,
            })
        submit = await ExamSubmitDAO.create_submit(self.db, exam_id, student.student_id,
                                                   total_score=total_score,
                                                   answers_json=answer_items,
                                                   submit_time=datetime.now(UTC))
        return exam_submit_to_dict(submit, exam=exam)

    async def my_submissions(self, user_id: int) -> list[dict]:
        student = await StudentDAO.get_by_user_id(self.db, user_id)
        if not student:
            raise ValueError("Student profile not found for current user")
        rows = await ExamSubmitDAO.get_by_student(self.db, student.student_id)
        result = []
        for submit in rows:
            exam = await ExamDAO.get_by_id(self.db, submit.exam_id)
            result.append(exam_submit_to_dict(submit, exam=exam))
        return result

    async def grade_submit(self, exam_submit_id: int, total_score: float,
                           teacher_comment: str | None = None) -> dict:
        submit = await ExamSubmitDAO.grade_submit(self.db, exam_submit_id, total_score, teacher_comment)
        if not submit:
            raise ValueError("Exam submit not found")
        exam = await ExamDAO.get_by_id(self.db, submit.exam_id)
        return exam_submit_to_dict(submit, exam=exam)
