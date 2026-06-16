"""教学班服务。

前端选课页面依赖教学班返回 course_name、teacher_name、容量、周次、地点、schedules 等字段。
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.courseDao import CourseDAO
from app.dao.teacherDao import TeacherDAO
from app.dao.teachingClassDao import TeachingClassDAO
from app.dao.enrollmentDao import CourseEnrollmentDAO
from app.dao.studentDao import StudentDAO
from app.services._helpers import teaching_class_to_dict, enrollment_to_dict, student_to_dict


class TeachingClassService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _normalize_schedule(item: dict) -> dict:
        """兼容前端可能传入的不同排课字段。

        推荐格式：{"weekday": 1, "start_time": "08:00", "end_time": "09:40"}
        旧格式：{"day": 1, "time": "08:00-09:40"}
        """
        if not isinstance(item, dict):
            raise ValueError("Each schedule must be an object")
        weekday = item.get("weekday", item.get("day"))
        start_time = item.get("start_time")
        end_time = item.get("end_time")
        if (not start_time or not end_time) and item.get("time"):
            parts = str(item["time"]).split("-")
            if len(parts) == 2:
                start_time, end_time = parts[0].strip(), parts[1].strip()
        if weekday is None or not start_time or not end_time:
            raise ValueError("Schedule must include weekday/start_time/end_time")
        return {"weekday": int(weekday), "start_time": str(start_time), "end_time": str(end_time)}

    @staticmethod
    def _weeks_overlap(start1: int, end1: int, start2: int, end2: int) -> bool:
        return start1 <= end2 and start2 <= end1

    @staticmethod
    def _times_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
        return start1 < end2 and start2 < end1

    async def _check_teacher_schedule_conflict(self, teacher_id: int, semester: str,
                                               schedules: list[dict], start_week: int,
                                               end_week: int, exclude_class_id: int | None = None) -> bool:
        existing_classes = await TeachingClassDAO.get_by_teacher(self.db, teacher_id)
        for old in existing_classes:
            if exclude_class_id and old.class_id == exclude_class_id:
                continue
            if old.semester != semester or old.status not in {"open", "closed"}:
                continue
            if not self._weeks_overlap(old.start_week, old.end_week, start_week, end_week):
                continue
            for old_s in old.schedules or []:
                old_norm = self._normalize_schedule(old_s)
                for new_s in schedules:
                    if old_norm["weekday"] == new_s["weekday"] and self._times_overlap(
                        old_norm["start_time"], old_norm["end_time"], new_s["start_time"], new_s["end_time"]
                    ):
                        return True
        return False

    async def create_teaching_class(self, course_id: int, teacher_id: int, semester: str,
                                    class_name: str, capacity: int, start_week: int,
                                    end_week: int, schedules: list[dict],
                                    location: str | None = None, status: str = "open") -> dict:
        if status not in {"open", "closed", "cancelled", "finished"}:
            raise ValueError("Invalid class status")
        if capacity <= 0:
            raise ValueError("Capacity must be greater than 0")
        if start_week <= 0 or end_week < start_week:
            raise ValueError("Invalid week range")
        course = await CourseDAO.get_by_id(self.db, course_id)
        if not course:
            raise ValueError("Course not found")
        teacher = await TeacherDAO.get_by_id(self.db, teacher_id)
        if not teacher:
            raise ValueError("Teacher not found")
        normalized = [self._normalize_schedule(item) for item in (schedules or [])]
        if not normalized:
            raise ValueError("Schedules must be a non-empty list")
        if await self._check_teacher_schedule_conflict(teacher_id, semester, normalized, start_week, end_week):
            raise ValueError("Teacher has schedule conflict")
        tc = await TeachingClassDAO.create_class(
            self.db,
            course_id=course_id,
            teacher_id=teacher_id,
            semester=semester,
            schedules=normalized,
            class_name=class_name,
            capacity=capacity,
            start_week=start_week,
            end_week=end_week,
            location=location,
            status=status,
        )
        return teaching_class_to_dict(tc, course=course, teacher=teacher)

    async def get_teaching_class(self, class_id: int) -> dict:
        tc = await TeachingClassDAO.get_by_id(self.db, class_id)
        if not tc:
            raise ValueError("Teaching class not found")
        course = await CourseDAO.get_by_id(self.db, tc.course_id)
        teacher = await TeacherDAO.get_by_id(self.db, tc.teacher_id)
        return teaching_class_to_dict(tc, course=course, teacher=teacher)

    async def list_classes(self, status: str | None = None, semester: str | None = None,
                           teacher_id: int | None = None, course_id: int | None = None) -> list[dict]:
        if teacher_id is not None:
            rows = await TeachingClassDAO.get_by_teacher(self.db, teacher_id, status=status)
        elif course_id is not None:
            rows = await TeachingClassDAO.get_by_course(self.db, course_id, status=status)
        elif semester is not None:
            rows = await TeachingClassDAO.get_by_semester(self.db, semester, status=status)
        else:
            rows = await TeachingClassDAO.get_all(self.db, status=status)
        result = []
        for tc in rows:
            course = await CourseDAO.get_by_id(self.db, tc.course_id)
            teacher = await TeacherDAO.get_by_id(self.db, tc.teacher_id)
            result.append(teaching_class_to_dict(tc, course=course, teacher=teacher))
        return result

    async def list_available_classes(self) -> list[dict]:
        return await self.list_classes(status="open")

    async def update_teaching_class(self, class_id: int, **kwargs) -> dict:
        tc = await TeachingClassDAO.get_by_id(self.db, class_id)
        if not tc:
            raise ValueError("Teaching class not found")
        allowed = {"course_id", "teacher_id", "semester", "class_name", "capacity", "location", "start_week", "end_week", "status", "schedules"}
        data = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        new_capacity = data.get("capacity", tc.capacity)
        start_week = data.get("start_week", tc.start_week)
        end_week = data.get("end_week", tc.end_week)
        if new_capacity <= 0 or new_capacity < tc.current_count:
            raise ValueError("Invalid capacity")
        if start_week <= 0 or end_week < start_week:
            raise ValueError("Invalid week range")
        if "status" in data and data["status"] not in {"open", "closed", "cancelled", "finished"}:
            raise ValueError("Invalid class status")
        if "schedules" in data:
            data["schedules"] = [self._normalize_schedule(item) for item in data["schedules"]]
        check_schedules = data.get("schedules", tc.schedules or [])
        if await self._check_teacher_schedule_conflict(data.get("teacher_id", tc.teacher_id), data.get("semester", tc.semester),
                                                       check_schedules, start_week, end_week, exclude_class_id=class_id):
            raise ValueError("Teacher has schedule conflict")
        updated = await TeachingClassDAO.update_class(self.db, class_id, **data)
        course = await CourseDAO.get_by_id(self.db, updated.course_id)
        teacher = await TeacherDAO.get_by_id(self.db, updated.teacher_id)
        return teaching_class_to_dict(updated, course=course, teacher=teacher)

    async def update_status(self, class_id: int, status: str) -> dict:
        if status not in {"open", "closed", "cancelled", "finished"}:
            raise ValueError("Invalid class status")
        tc = await TeachingClassDAO.update_status(self.db, class_id, status)
        if not tc:
            raise ValueError("Teaching class not found")
        return await self.get_teaching_class(class_id)

    async def delete_class(self, class_id: int) -> bool:
        ok = await TeachingClassDAO.soft_delete(self.db, class_id)
        if not ok:
            raise ValueError("Teaching class not found")
        return ok

    async def get_class_students(self, class_id: int) -> list[dict]:
        tc = await TeachingClassDAO.get_by_id(self.db, class_id)
        if not tc:
            raise ValueError("Teaching class not found")
        enrollments = await CourseEnrollmentDAO.get_by_class(self.db, class_id, status="enrolled")
        result = []
        for e in enrollments:
            student = await StudentDAO.get_by_id(self.db, e.student_id)
            if student:
                item = student_to_dict(student)
                item.update(enrollment_to_dict(e))
                result.append(item)
        return result
