from pydantic import BaseModel, Field


class CreateKnowledgePointRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    subject: str = Field(min_length=1, max_length=50)
    description: str | None = None
    parent_id: int | None = None
    difficulty: int = Field(default=1, ge=1, le=5)
