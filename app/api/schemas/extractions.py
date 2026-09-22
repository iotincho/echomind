"""HTTP contracts for explicitly triggered document extraction."""

from pydantic import BaseModel, Field


class CreateExtractionRequest(BaseModel):
    profile: str = Field(default="v3", min_length=1)
