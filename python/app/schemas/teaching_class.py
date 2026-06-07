from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

from app.schemas.class_schedule import ClassScheduleCreate


class TeachingClassCreate(BaseModel):
    course_id: int
    semester: str
    class_name: str
    capacity: int
    start_date: date
    end_date: date


class TeachingClassCreateWithTeacher(TeachingClassCreate):
    teacher_id: int
    schedules: list[ClassScheduleCreate] = Field(default_factory=list)


class TeachingClassUpdate(BaseModel):
    class_name: Optional[str] = None
    capacity: Optional[int] = None


class TeachingClassResponse(BaseModel):
    class_id: int
    course_id: int
    teacher_id: int
    semester: str
    class_name: str
    capacity: int
    current_count: int
    start_date: date
    end_date: date
    status: str

    class Config:
        from_attributes = True


class TeachingClassDetail(TeachingClassResponse):
    course_name: Optional[str] = None
    teacher_name: Optional[str] = None
    schedules: list = Field(default_factory=list)
