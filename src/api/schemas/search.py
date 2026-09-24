"""HTTP contracts for semantic retrieval of evidence-backed claims."""

from pydantic import BaseModel, Field


class SearchClaimsRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=50)


class SearchRequest(SearchClaimsRequest):
    """Request a mixed, score-ordered result set of claims and documents."""
