from pydantic import BaseModel, Field


class SubmitAnswerRequest(BaseModel):
    user_id: int
    question_id: int
    user_answer: str
    quality_q: int = Field(default=5, ge=0, le=5)
    time_spent_seconds: float | None = None


class TutorAskRequest(BaseModel):
    user_id: int
    knowledge_id: int
    question: str = Field(min_length=1, max_length=2000)


class TutorMessageRequest(BaseModel):
    user_id: int
    message: str = Field(min_length=1, max_length=2000)
    knowledge_id: int | None = None


class HintRequest(BaseModel):
    user_id: int
    knowledge_id: int
    question_id: int | None = None


class ExplanationRequest(BaseModel):
    user_id: int
    knowledge_id: int
    question: str = Field(default="", max_length=2000)
    user_answer: str = Field(default="", max_length=2000)
    correct_answer: str = Field(default="", max_length=2000)
    is_correct: bool | None = None
