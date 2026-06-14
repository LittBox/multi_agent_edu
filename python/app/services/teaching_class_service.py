from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, time
from app.dao.teachingClassDao import TeachingClassDAO
from app.dao.courseDao import CourseDAO
from app.dao.teacherDao import TeacherDAO
from app.dao.enrollmentDao import CourseEnrollmentDAO

"""
教学班服务类，提供与教学班相关的业务逻辑处理，包括创建教学班、查询教学班信息、更新教学班信息、关闭教学班等功能。
教学班服务类的主要职责包括：
1. 创建教学班：根据课程ID、教师ID、学期、班级名称、容量、上课日期等信息创建新的教学班，并检查教师的时间安排是否有冲突。
2. 查询教学班信息：根据教学班ID查询教学班的详细信息，包括所属课程、授课教师、学期、班级名称、容量、当前人数、上课时间安排等信息。
3. 更新教学班信息：根据教学班ID更新教学班的相关信息，例如修改班级名称、调整容量、变更上课日期等，并检查更新后的信息是否合理。
4. 关闭教学班：根据教学班ID和教师ID关闭教学班，只有授课教师可以关闭教学班，并且只能关闭状态为“open”的教学班。
5. 获取教学班学生列表：根据教学班ID获取已选该教学班的学生列表，包括学生ID、姓名、学号等信息。
教学班服务类通过调用数据访问对象（DAO）来与数据库进行交互，确保业务逻辑的正确性和数据的一致性。同时，教学班服务类还负责处理业务逻辑中的各种异常情况，例如教师时间冲突、教学班不存在、容量不足等，并返回相应的错误信息给调用方。
"""
class TeachingClassService:
    def __init__(self, db: AsyncSession):
        self.db = db

    """
    查看老师安排是否有冲突的选课时间
    1. 获取老师在该学期的所有教学班。
    2. 获取每个教学班的上课时间安排。
    3. 对比新教学班的上课时间安排与现有教学班的上课时间安排，检查是否有时间冲突。
    4. 如果有冲突，返回冲突信息；如果没有冲突，允许创建新的教学班。
    """
    async def _check_teacher_schedule_conflict(
        self,
        teacher_id: int,
        semester: str,
        schedules: list,
        start_week: int,
        end_week: int,
    ) -> bool:
        existing_classes = await TeachingClassDAO.get_by_teacher_semester(
            self.db,
            teacher_id,
            semester,
        )

        for existing_class in existing_classes:
            if existing_class.status not in ("open", "closed"):
                continue

            if not self._weeks_overlap(
                existing_class.start_week,
                existing_class.end_week,
                start_week,
                end_week,
            ):
                continue

            existing_schedules = existing_class.schedules or []

            for existing_sched in existing_schedules:
                for new_sched in schedules:
                    if existing_sched.get("day") != new_sched.get("day"):
                        continue

                    old_time = existing_sched.get("time")
                    new_time = new_sched.get("time")

                    if old_time and new_time and self._times_overlap(old_time, new_time):
                        return True

        return False
    #静态方法用于检查两个时间段是否重叠，两个时间段重叠的条件是：
    #第一个时间段的开始时间早于第二个时间段的结束时间，并且第二个时间段的开始时间早于第一个时间段的结束时间
    @staticmethod
    def _weeks_overlap(start1: int, end1: int, start2: int, end2: int) -> bool:
        return start1 <= end2 and start2 <= end1

    #静态方法用于检查两个时间段是否重叠，两个时间段重叠的条件是：
    #第一个时间段的开始时间早于第二个时间段的结束时间，并且第二个时间段的开始时间早于第一个时间段的结束时间
    @staticmethod
    def _times_overlap(time_range1: str, time_range2: str) -> bool:
        start1, end1 = time_range1.split("-")
        start2, end2 = time_range2.split("-")

        start1 = start1.strip()
        end1 = end1.strip()
        start2 = start2.strip()
        end2 = end2.strip()

        return start1 < end2 and start2 < end1
    
    """
    创建教学班
    1. 验证教师和课程的存在性。
    2. 验证教学班容量和上课日期的合理性。
    3. 检查教师的时间安排是否有冲突。
    4. 创建教学班记录，并返回创建结果。
    """
    async def create_teaching_class(
        self,
        course_id: int,
        teacher_id: int,
        semester: str,
        class_name: str,
        capacity: int,
        start_week: int,
        end_week: int,
        schedules: list,
        location: str | None = None,
    ):
        teacher = await TeacherDAO.get_by_id(self.db, teacher_id)
        if not teacher:
            raise ValueError("Teacher not found")

        course = await CourseDAO.get_by_id(self.db, course_id)
        if not course:
            raise ValueError("Course not found")

        if capacity <= 0:
            raise ValueError("Capacity must be greater than 0")

        if start_week <= 0:
            raise ValueError("Start week must be positive")

        if end_week < start_week:
            raise ValueError("End week must be greater than or equal to start week")

        if not isinstance(schedules, list) or len(schedules) == 0:
            raise ValueError("Schedules must be a non-empty list")

        for sched in schedules:
            if not isinstance(sched, dict):
                raise ValueError("Each schedule must be an object")
            if "day" not in sched:
                raise ValueError("Each schedule must include day")
            if "time" not in sched:
                raise ValueError("Each schedule must include time")
            if "-" not in sched["time"]:
                raise ValueError("Schedule time must be like '10:00-11:00'")

        if await self._check_teacher_schedule_conflict(
            teacher_id=teacher_id,
            semester=semester,
            schedules=schedules,
            start_week=start_week,
            end_week=end_week,
        ):
            raise ValueError("Teacher has schedule conflict")

        teaching_class = await TeachingClassDAO.create_class(
            self.db,
            course_id=course_id,
            teacher_id=teacher_id,
            semester=semester,
            class_name=class_name,
            capacity=capacity,
            start_week=start_week,
            end_week=end_week,
            location=location,
            schedules=schedules,
        )

        return teaching_class
    
    """
    根据教学班ID查询教学班信息
    """
    async def get_teaching_class(self, class_id: int):
        teaching_class = await TeachingClassDAO.get_by_id(self.db, class_id)
        if not teaching_class:
            raise ValueError("Teaching class not found")
        return teaching_class

    """
    获取所有教学班信息，包括：
        1. 教学班ID
        2. 所属课程ID和课程名称
        3. 授课教师ID和教师姓名
        4. 学期
        5. 班级名称
        6. 教学班容量
        7. 当前选课人数
        8. 上课时间安排（包括星期几、开始时间、结束时间、上课地点、上课周数等信息）
    """
    async def get_all_classes(self):
        return await TeachingClassDAO.get_all(self.db)


    """
    根据教学班id查询教学班日常安排信息，包括：
    1. 上课的星期几    2. 上课的开始时间和结束时间
    3. 上课地点    4. 上课周数  
    """
    async def get_class_schedules(self, class_id: int):
        return await ClassScheduleDAO.get_by_class(self.db, class_id)

    """
    根据教师ID和学期查询教师的教学班信息，
    返回该教师在指定学期的所有教学班列表，包括：
    教学班ID、课程名称、班级名称、容量、当前人数、上课时间安排等信息。
    """
    async def get_teacher_classes(self, teacher_id: int, semester: str | None = None):
        if semester:
            return await TeachingClassDAO.get_by_teacher_semester(
                self.db, teacher_id, semester
            )
        return await TeachingClassDAO.get_by_teacher(self.db, teacher_id)

    
    """
    关闭教学班，只有授课教师可以关闭教学班，并且只能关闭状态为“open”的教学班。
    1. 验证教学班的存在性。
    2. 验证教师的权限。
    3. 验证教学班的状态。
    4. 更新教学班状态为“closed”，并返回操作结果。
    """
    async def close_class(self, class_id: int, teacher_id: int):
        teaching_class = await TeachingClassDAO.get_by_id(self.db, class_id)
        if not teaching_class:
            raise ValueError("Teaching class not found")

        if teaching_class.teacher_id != teacher_id:
            raise ValueError("Only the assigned teacher can close this class")

        if teaching_class.status != "open":
            raise ValueError("Only open classes can be closed")

        await TeachingClassDAO.update_status(self.db, class_id, "closed")
        return {"message": "Class closed successfully"}


    """
    根据教学班id更新教学班信息，例如修改班级名称、调整容量、变更上课日期等，并检查更新后的信息是否合理。
    1. 验证教学班的存在性。
    2. 验证更新后的容量和上课日期的合理性。
    3. 更新教学班记录，并返回更新结果。
    """
    async def update_teaching_class(self, class_id: int, **kwargs):
        teaching_class = await TeachingClassDAO.get_by_id(self.db, class_id)
        if not teaching_class:
            raise ValueError("Teaching class not found")

        capacity = kwargs.get("capacity")
        if capacity is not None:
            if capacity <= 0:
                raise ValueError("Capacity must be greater than 0")
            if capacity < teaching_class.current_count:
                raise ValueError("Capacity cannot be lower than current enrollment")

        start_week = kwargs.get("start_week", teaching_class.start_week)
        end_week = kwargs.get("end_week", teaching_class.end_week)
        if start_week is not None and start_week <= 0:
            raise ValueError("Start week must be positive")
        if start_week is not None and end_week is not None and end_week < start_week:
            raise ValueError("End week must be greater than or equal to start week")

        updated = await TeachingClassDAO.update_class(self.db, class_id, **kwargs)
        if not updated:
            raise ValueError("Teaching class not found")
        return updated

    """
    根据教学班id查询该教学班的所有学生信息。
    """
    async def get_class_students(self, class_id: int):
        teaching_class = await TeachingClassDAO.get_by_id(self.db, class_id)
        if not teaching_class:
            raise ValueError("Teaching class not found")

        return await CourseEnrollmentDAO.get_by_class(self.db, class_id)
