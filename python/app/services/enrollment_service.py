"""学生选课服务。

本服务直接对应学生选课前端：
- list_available_classes：上方公开课程卡片
- list_my_enrollments：下方我已选择课程卡片
- enroll_student：加入课程
- drop_student：退课
"""
from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.courseDao import CourseDAO
from app.dao.enrollmentDao import CourseEnrollmentDAO
from app.dao.studentDao import StudentDAO
from app.dao.teacherDao import TeacherDAO
from app.dao.teachingClassDao import TeachingClassDAO
from app.services._helpers import teaching_class_to_dict, enrollment_to_dict


class EnrollmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _normalize_schedule(item: dict) -> dict:
        weekday = item.get("weekday", item.get("day"))
        start_time = item.get("start_time")
        end_time = item.get("end_time")
        if (not start_time or not end_time) and item.get("time"):
            parts = str(item["time"]).split("-")
            if len(parts) == 2:
                start_time, end_time = parts[0].strip(), parts[1].strip()
        return {"weekday": weekday, "start_time": str(start_time), "end_time": str(end_time)}

    @staticmethod
    def _times_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
        return start1 < end2 and start2 < end1

    @staticmethod
    def _weeks_overlap(start1: int, end1: int, start2: int, end2: int) -> bool:
        return start1 <= end2 and start2 <= end1

    async def _check_time_conflict(self, student_id: int, new_class) -> bool:
        enrollments = await CourseEnrollmentDAO.get_by_student(self.db, student_id, status="enrolled")
        for e in enrollments:
            old_class = await TeachingClassDAO.get_by_id(self.db, e.class_id)
            if not old_class:
                continue
            if not self._weeks_overlap(old_class.start_week, old_class.end_week, new_class.start_week, new_class.end_week):
                continue
            for old_s in old_class.schedules or []:
                old_norm = self._normalize_schedule(old_s)
                for new_s in new_class.schedules or []:
                    new_norm = self._normalize_schedule(new_s)
                    if old_norm["weekday"] == new_norm["weekday"] and self._times_overlap(
                        old_norm["start_time"], old_norm["end_time"], new_norm["start_time"], new_norm["end_time"]
                    ):
                        return True
        return False

    async def enroll_student(self, student_id: int, class_id: int) -> dict:
        student = await StudentDAO.get_by_id(self.db, student_id)
        if not student:
            raise ValueError("Student not found")
        tc = await TeachingClassDAO.get_by_id(self.db, class_id)
        if not tc:
            raise ValueError("Teaching class not found")
        if tc.status != "open":
            raise ValueError("Class is not open for enrollment")
        if tc.current_count >= tc.capacity:
            raise ValueError("Class is full")
        if await CourseEnrollmentDAO.get_active_enrollment(self.db, student_id, class_id):
            raise ValueError("Student already enrolled in this class")
        for e in await CourseEnrollmentDAO.get_by_student(self.db, student_id, status="enrolled"):
            other = await TeachingClassDAO.get_by_id(self.db, e.class_id)
            if other and other.course_id == tc.course_id:
                raise ValueError("Student already enrolled in another class of the same course")
        if await self._check_time_conflict(student_id, tc):
            raise ValueError("Student has time conflict with other enrolled classes")
        enrollment = await CourseEnrollmentDAO.create_enrollment(self.db, class_id, student_id)
        await TeachingClassDAO.increment_count(self.db, class_id)
        course = await CourseDAO.get_by_id(self.db, tc.course_id)
        teacher = await TeacherDAO.get_by_id(self.db, tc.teacher_id)
        return enrollment_to_dict(enrollment, tc=tc, course=course, teacher=teacher)

    async def enroll_by_user(self, user_id: int, class_id: int) -> dict:
        student = await StudentDAO.get_by_user_id(self.db, user_id)
        if not student:
            raise ValueError("Student profile not found for current user")
        return await self.enroll_student(student.student_id, class_id)

    async def drop_student(self, enrollment_id: int, student_id: int,
                           drop_reason: str | None = "学生主动退课") -> dict:
        enrollment = await CourseEnrollmentDAO.get_by_id(self.db, enrollment_id)
        if not enrollment:
            raise ValueError("Enrollment not found")
        if enrollment.student_id != student_id:
            raise ValueError("Can only drop your own enrollment")
        if enrollment.enroll_status != "enrolled":
            raise ValueError("Enrollment is not active")
        updated = await CourseEnrollmentDAO.drop_enrollment(self.db, enrollment_id, drop_reason=drop_reason)
        await TeachingClassDAO.decrement_count(self.db, enrollment.class_id)
        tc = await TeachingClassDAO.get_by_id(self.db, updated.class_id)
        course = await CourseDAO.get_by_id(self.db, tc.course_id) if tc else None
        teacher = await TeacherDAO.get_by_id(self.db, tc.teacher_id) if tc else None
        return enrollment_to_dict(updated, tc=tc, course=course, teacher=teacher)

    async def drop_by_user(self, user_id: int, enrollment_id: int,
                           drop_reason: str | None = "学生主动退课") -> dict:
        student = await StudentDAO.get_by_user_id(self.db, user_id)
        if not student:
            raise ValueError("Student profile not found for current user")
        return await self.drop_student(enrollment_id, student.student_id, drop_reason)

    async def list_available_classes(self) -> list[dict]:
        rows = await TeachingClassDAO.get_all_open(self.db)
        result = []
        for tc in rows:
            course = await CourseDAO.get_by_id(self.db, tc.course_id)
            teacher = await TeacherDAO.get_by_id(self.db, tc.teacher_id)
            result.append(teaching_class_to_dict(tc, course=course, teacher=teacher))
        return result

    async def list_my_enrollments(self, user_id: int, status: str | None = "enrolled") -> list[dict]:
        student = await StudentDAO.get_by_user_id(self.db, user_id)
        if not student:
            raise ValueError("Student profile not found for current user")
        enrollments = await CourseEnrollmentDAO.get_by_student(self.db, student.student_id, status=status)
        result = []
        for e in enrollments:
            tc = await TeachingClassDAO.get_by_id(self.db, e.class_id)
            course = await CourseDAO.get_by_id(self.db, tc.course_id) if tc else None
            teacher = await TeacherDAO.get_by_id(self.db, tc.teacher_id) if tc else None
            result.append(enrollment_to_dict(e, tc=tc, course=course, teacher=teacher))
        return result

    async def update_score(self, enrollment_id: int, course_score: float | None) -> dict:
        if course_score is not None and not (0 <= course_score <= 100):
            raise ValueError("Course score must be between 0 and 100")
        enrollment = await CourseEnrollmentDAO.update_score(self.db, enrollment_id, course_score)
        if not enrollment:
            raise ValueError("Enrollment not found")
        return enrollment_to_dict(enrollment)
