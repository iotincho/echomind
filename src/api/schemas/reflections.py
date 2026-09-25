"""HTTP contract for evidence-bound reflection."""

from pydantic import BaseModel, Field


class ResolveQuestionRequest(BaseModel):
    question: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=50)
    profile_name: str = Field(default="v1", min_length=1)
