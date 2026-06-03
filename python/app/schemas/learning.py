from pydantic import BaseModel


class SubmitAnswerRequest(BaseModel):
    user_id: int
    question_id: int
    user_answer: str
    quality_q: int = 5


class AskQuestionRequest(BaseModel):
    learner_id: str
    knowledge_id: str
    question: str


class SendMessageRequest(BaseModel):
    learner_id: str
    message: str
    knowledge_id: str = "general"