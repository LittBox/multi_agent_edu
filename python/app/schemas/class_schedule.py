from pydantic import BaseModel
from typing import Optional
from datetime import time


class ClassScheduleCreate(BaseModel):
    weekday: int
    start_time: time
    end_time: time
    week_start: int
    week_end: int
    classroom: Optional[str] = None


class ClassScheduleResponse(BaseModel):
    schedule_id: int
    class_id: int
    weekday: int
    start_time: time
    end_time: time
    classroom: Optional[str]
    week_start: int
    week_end: int

    class Config:
        from_attributes = True
