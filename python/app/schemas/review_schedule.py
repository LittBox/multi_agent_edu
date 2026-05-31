from pydantic import BaseModel
from datetime import datetime


class ReviewScheduleResponse(BaseModel):
    knowledge_id: int

    interval_days: int
    ef: float

    next_review_at: datetime

    model_config = {
        "from_attributes": True
    }