"""Service 层通用辅助函数。

这些函数不直接暴露给 router，只负责把 SQLAlchemy model 对象转换成
前端更容易消费的 dict，并统一处理 datetime 序列化。
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any


def iso(value: Any) -> str | None:
    """把 datetime/date 转成 ISO 字符串，空值返回 None。"""
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def safe_float(value: Any) -> float | None:
    """把数据库里的数值转为 float，空值保持 None。"""
    return None if value is None else float(value)


def user_to_dict(user) -> dict:
    """用户对象序列化。注意：永远不返回 pwd 密文字段。"""
    return {
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role,
        "email": user.email,
        "avatar": user.avatar,
        "status": user.status,
        "created_at": iso(user.created_at),
        "updated_at": iso(user.updated_at),
    }


def student_to_dict(student) -> dict:
    return {
        "student_id": student.student_id,
        "user_id": student.user_id,
        "student_no": student.student_no,
        "student_name": student.student_name,
        "major": student.major,
        "grade": student.grade,
        "class_name": student.class_name,
        "is_deleted": student.is_deleted,
        "created_at": iso(student.created_at),
        "updated_at": iso(student.updated_at),
    }


def teacher_to_dict(teacher) -> dict:
    return {
        "teacher_id": teacher.teacher_id,
        "user_id": teacher.user_id,
        "teacher_no": teacher.teacher_no,
        "teacher_name": teacher.teacher_name,
        "department": teacher.department,
        "title": teacher.title,
        "is_deleted": teacher.is_deleted,
        "created_at": iso(teacher.created_at),
        "updated_at": iso(teacher.updated_at),
    }


def course_to_dict(course, teacher_name: str | None = None) -> dict:
    return {
        "course_id": course.course_id,
        "course_code": course.course_code,
        "course_name": course.course_name,
        "credit": safe_float(course.credit),
        "description": course.description,
        "created_by_teacher_id": course.created_by_teacher_id,
        "teacher_name": teacher_name,
        "status": course.status,
        "is_deleted": course.is_deleted,
        "created_at": iso(course.created_at),
        "updated_at": iso(course.updated_at),
    }


def teaching_class_to_dict(tc, course=None, teacher=None) -> dict:
    return {
        "class_id": tc.class_id,
        "course_id": tc.course_id,
        "course_code": getattr(course, "course_code", None),
        "course_name": getattr(course, "course_name", None),
        "teacher_id": tc.teacher_id,
        "teacher_name": getattr(teacher, "teacher_name", None),
        "semester": tc.semester,
        "class_name": tc.class_name,
        "capacity": tc.capacity,
        "current_count": tc.current_count,
        "location": tc.location,
        "start_week": tc.start_week,
        "end_week": tc.end_week,
        "status": tc.status,
        "schedules": tc.schedules or [],
        "is_deleted": tc.is_deleted,
        "created_at": iso(tc.created_at),
        "updated_at": iso(tc.updated_at),
    }


def enrollment_to_dict(enrollment, tc=None, course=None, teacher=None) -> dict:
    data = {
        "enrollment_id": enrollment.enrollment_id,
        "class_id": enrollment.class_id,
        "student_id": enrollment.student_id,
        "enroll_status": enrollment.enroll_status,
        "enrolled_at": iso(enrollment.enrolled_at),
        "dropped_at": iso(enrollment.dropped_at),
        "drop_reason": enrollment.drop_reason,
        "course_score": safe_float(enrollment.course_score),
        "is_deleted": enrollment.is_deleted,
        "created_at": iso(enrollment.created_at),
        "updated_at": iso(enrollment.updated_at),
    }
    if tc is not None:
        data.update(teaching_class_to_dict(tc, course=course, teacher=teacher))
        data["enrollment_id"] = enrollment.enrollment_id
        data["student_id"] = enrollment.student_id
        data["enroll_status"] = enrollment.enroll_status
        data["enrolled_at"] = iso(enrollment.enrolled_at)
        data["dropped_at"] = iso(enrollment.dropped_at)
        data["drop_reason"] = enrollment.drop_reason
        data["course_score"] = safe_float(enrollment.course_score)
    return data


def knowledge_to_dict(kp) -> dict:
    return {
        "knowledge_id": kp.knowledge_id,
        "name": kp.name,
        "subject": kp.subject,
        "description": kp.description or "",
        "parent_id": kp.parent_id,
        "difficulty": kp.difficulty,
        "created_at": iso(kp.created_at),
    }


def question_to_dict(question, include_answer: bool = False) -> dict:
    data = {
        "question_id": question.question_id,
        "knowledge_id": question.knowledge_id,
        "question_type": question.question_type,
        "stem": question.stem,
        "option_a": question.option_a,
        "option_b": question.option_b,
        "option_c": question.option_c,
        "option_d": question.option_d,
        "explanation": question.explanation if include_answer else None,
        "difficulty": question.difficulty,
        "image_url": question.image_url,
        "created_at": iso(question.created_at),
    }
    if include_answer:
        data["answer"] = question.answer
    return data


def exam_to_dict(exam, course=None, teacher=None) -> dict:
    return {
        "exam_id": exam.exam_id,
        "title": exam.title,
        "course_id": exam.course_id,
        "course_name": getattr(course, "course_name", None),
        "teacher_id": exam.teacher_id,
        "teacher_name": getattr(teacher, "teacher_name", None),
        "duration_minutes": exam.duration_minutes,
        "exam_type": exam.exam_type,
        "start_time": iso(exam.start_time),
        "end_time": iso(exam.end_time),
        "status": exam.status,
        "is_deleted": exam.is_deleted,
        "created_at": iso(exam.created_at),
        "updated_at": iso(exam.updated_at),
    }


def exam_question_to_dict(eq, question=None, include_answer: bool = False) -> dict:
    data = {
        "exam_question_id": eq.exam_question_id,
        "exam_id": eq.exam_id,
        "question_id": eq.question_id,
        "score": safe_float(eq.score),
        "sort_order": eq.sort_order,
    }
    if question is not None:
        data.update(question_to_dict(question, include_answer=include_answer))
        data["exam_question_id"] = eq.exam_question_id
        data["exam_id"] = eq.exam_id
        data["score"] = safe_float(eq.score)
        data["sort_order"] = eq.sort_order
    return data


def exam_submit_to_dict(submit, exam=None) -> dict:
    return {
        "exam_submit_id": submit.exam_submit_id,
        "exam_id": submit.exam_id,
        "exam_title": getattr(exam, "title", None),
        "student_id": submit.student_id,
        "submit_time": iso(submit.submit_time),
        "total_score": safe_float(submit.total_score),
        "teacher_comment": submit.teacher_comment,
        "answers_json": submit.answers_json,
        "created_at": iso(submit.created_at),
        "updated_at": iso(submit.updated_at),
    }


def task_bank_to_dict(task, course=None, teacher=None) -> dict:
    return {
        "task_id": task.task_id,
        "course_id": task.course_id,
        "course_name": getattr(course, "course_name", None),
        "teacher_id": task.teacher_id,
        "teacher_name": getattr(teacher, "teacher_name", None),
        "task_type": task.task_type,
        "task_content": task.task_content,
        "is_deleted": task.is_deleted,
        "created_at": iso(task.created_at),
        "updated_at": iso(task.updated_at),
    }


def task_release_to_dict(release, task=None, course=None, teacher=None) -> dict:
    data = {
        "task_publish_id": release.task_publish_id,
        "task_id": release.task_id,
        "publish_time": iso(release.publish_time),
        "deadline": iso(release.deadline),
        "is_deleted": release.is_deleted,
        "created_at": iso(release.created_at),
        "updated_at": iso(release.updated_at),
    }
    if task is not None:
        data.update({
            "course_id": task.course_id,
            "course_name": getattr(course, "course_name", None),
            "teacher_id": task.teacher_id,
            "teacher_name": getattr(teacher, "teacher_name", None),
            "task_type": task.task_type,
            "task_content": task.task_content,
        })
    return data


def task_submission_to_dict(submission, release=None, task=None) -> dict:
    data = {
        "submit_id": submission.submit_id,
        "task_publish_id": submission.task_publish_id,
        "student_id": submission.student_id,
        "submit_time": iso(submission.submit_time),
        "answer_content": submission.answer_content,
        "score": safe_float(submission.score),
        "comment": submission.comment,
        "created_at": iso(submission.created_at),
        "updated_at": iso(submission.updated_at),
    }
    if release is not None:
        data["task_id"] = release.task_id
        data["deadline"] = iso(release.deadline)
    if task is not None:
        data["task_content"] = task.task_content
        data["course_id"] = task.course_id
        data["task_type"] = task.task_type
    return data
