from pydantic import BaseModel


class SubmitAnswerRequest(BaseModel):
    user_id: int
    question_id: int

    user_answer: str

    started_at: str | None = None