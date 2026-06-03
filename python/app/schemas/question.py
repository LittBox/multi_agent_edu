from datetime import datetime
from typing import Any

from pydantic import BaseModel


class QuestionCreate(BaseModel):
    knowledge_id: int
    question_type: str
    stem: str
    option_a: str | None = None
    option_b: str | None = None
    option_c: str | None = None
    option_d: str | None = None
    answer: str
    explanation: str | None = None
    difficulty: int = 1
    image_url: str | None = None


class QuestionResponse(BaseModel):
    question_id: int
    knowledge_id: int
    question_type: str
    stem: str
    option_a: str | None = None
    option_b: str | None = None
    option_c: str | None = None
    option_d: str | None = None
    answer: str
    explanation: str | None
    difficulty: int
    image_url: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }