from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CourseEnrollmentCreate(BaseModel):
    class_id: int


class CourseEnrollmentResponse(BaseModel):
    enrollment_id: int
    class_id: int
    student_id: int
    enroll_status: str
    enrolled_at: datetime
    dropped_at: Optional[datetime]

    class Config:
        from_attributes = True


class EnrolledClassInfo(BaseModel):
    enrollment_id: int
    class_id: int
    course_name: str
    teacher_name: str
    semester: str
    class_name: str
    enroll_status: str
    enrolled_at: datetime
    schedules: list = Field(default_factory=list)
