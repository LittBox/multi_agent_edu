from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, UTC, date, time
from app.dao.enrollmentDao import CourseEnrollmentDAO
from app.dao.studentDao import StudentDAO
from app.dao.teachingClassDao import TeachingClassDAO
from app.dao.classScheduleDao import ClassScheduleDAO
from app.dao.courseDao import CourseDAO

"""
选课服务类，主要职责包括：
1. 学生选课
2. 检查选课时间冲突
3. 学生退课
4. 获取可选课程列表
5. 获取学生已选课程列表
"""
class EnrollmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _times_overlap(start1: time, end1: time, start2: time, end2: time) -> bool:
        return start1 < end2 and start2 < end1

    @staticmethod
    def _weeks_overlap(start1: int, end1: int, start2: int, end2: int) -> bool:
        return start1 <= end2 and start2 <= end1

    async def _check_time_conflict(
        self,
        student_id: int,
        new_schedules: list,
    ) -> bool:
        enrolled_classes = await CourseEnrollmentDAO.get_by_student(
            self.db, student_id, "enrolled"
        )

        for enrollment in enrolled_classes:
            existing_class = await TeachingClassDAO.get_by_id(
                self.db, enrollment.class_id
            )
            if not existing_class:
                continue

            existing_schedules = await ClassScheduleDAO.get_by_class(
                self.db, existing_class.class_id
            )

            for existing_sched in existing_schedules:
                for new_sched in new_schedules:
                    if (
                        existing_sched.weekday == new_sched["weekday"]
                        and self._weeks_overlap(
                            existing_sched.week_start,
                            existing_sched.week_end,
                            new_sched["week_start"],
                            new_sched["week_end"],
                        )
                        and self._times_overlap(
                            existing_sched.start_time,
                            existing_sched.end_time,
                            new_sched["start_time"],
                            new_sched["end_time"],
                        )
                    ):
                        return True
        return False

    """
    选课流程：
    1. 验证学生和教学班的存在性。
    2. 检查教学班是否开放选课，是否已满员。
    3. 检查学生是否已选该教学班，或已选同一课程的其他教学班。
    4. 检查选课时间是否在课程开始前，且没有与已选课程的时间冲突。
    5. 创建选课记录，并更新教学班的当前人数。
    6. 返回选课结果。
    """
    async def enroll_student(self, student_id: int, class_id: int):
        student = await StudentDAO.get_by_id(self.db, student_id)
        if not student:
            raise ValueError("Student not found")

        teaching_class = await TeachingClassDAO.get_by_id(self.db, class_id)
        if not teaching_class:
            raise ValueError("Teaching class not found")

        #检查教学班状态和容量，如果教学班不开放选课或者已满员，则拒绝选课请求
        if teaching_class.status != "open":
            raise ValueError("Class is not open for enrollment")

        if teaching_class.current_count >= teaching_class.capacity:
            raise ValueError("Class is full")

        already_enrolled = await CourseEnrollmentDAO.get_active_enrollment(
            self.db, student_id, class_id
        )
        if already_enrolled:
            raise ValueError("Student already enrolled in this class")

        other_enrollments = await CourseEnrollmentDAO.get_by_student(
            self.db, student_id, "enrolled"
        )
        for enrollment in other_enrollments:
            other_class = await TeachingClassDAO.get_by_id(self.db, enrollment.class_id)
            if other_class and other_class.course_id == teaching_class.course_id:
                raise ValueError("Student already enrolled in another class of the same course")

        today = date.today()
        if today >= teaching_class.start_date:
            raise ValueError("Cannot enroll after course start date")

        new_schedules = await ClassScheduleDAO.get_by_class(self.db, class_id)
        if await self._check_time_conflict(student_id, new_schedules):
            raise ValueError("Student has time conflict with other enrolled classes")

        enrollment = await CourseEnrollmentDAO.create_enrollment(
            self.db, class_id, student_id
        )

        await TeachingClassDAO.increment_count(self.db, class_id)

        return enrollment

    async def drop_student(self, enrollment_id: int, student_id: int):
        enrollment = await CourseEnrollmentDAO.get_by_id(self.db, enrollment_id)
        if not enrollment:
            raise ValueError("Enrollment not found")

        if enrollment.student_id != student_id:
            raise ValueError("Can only drop your own enrollment")

        if enrollment.enroll_status != "enrolled":
            raise ValueError("Can only drop active enrollments")

        teaching_class = await TeachingClassDAO.get_by_id(self.db, enrollment.class_id)
        if not teaching_class:
            raise ValueError("Teaching class not found")

        today = date.today()
        if today >= teaching_class.start_date:
            raise ValueError("Cannot drop after course start date")

        await CourseEnrollmentDAO.update_status(
            self.db, enrollment_id, "dropped", "Student withdrew"
        )

        await TeachingClassDAO.decrement_count(self.db, enrollment.class_id)

        return {"message": "Successfully dropped from class"}

    async def get_available_classes(self, student_id: int, semester: str | None = None):
        student = await StudentDAO.get_by_id(self.db, student_id)
        if not student:
            raise ValueError("Student not found")

        open_classes = await TeachingClassDAO.get_all_open(self.db)

        available = []
        for teaching_class in open_classes:
            if semester and teaching_class.semester != semester:
                continue

            if teaching_class.current_count >= teaching_class.capacity:
                continue

            already_enrolled = await CourseEnrollmentDAO.get_active_enrollment(
                self.db, student_id, teaching_class.class_id
            )
            if already_enrolled:
                continue

            other_enrollments = await CourseEnrollmentDAO.get_by_student(
                self.db, student_id, "enrolled"
            )
            has_same_course = False
            for enrollment in other_enrollments:
                other_class = await TeachingClassDAO.get_by_id(
                    self.db, enrollment.class_id
                )
                if (
                    other_class
                    and other_class.course_id == teaching_class.course_id
                ):
                    has_same_course = True
                    break

            if has_same_course:
                continue

            today = date.today()
            if today >= teaching_class.start_date:
                continue

            new_schedules = await ClassScheduleDAO.get_by_class(
                self.db, teaching_class.class_id
            )
            if await self._check_time_conflict(student_id, new_schedules):
                continue

            available.append(teaching_class)

        return available

    async def get_student_classes(self, student_id: int, status: str = "enrolled"):
        student = await StudentDAO.get_by_id(self.db, student_id)
        if not student:
            raise ValueError("Student not found")

        return await CourseEnrollmentDAO.get_by_student(self.db, student_id, status)
