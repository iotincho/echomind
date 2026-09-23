"""Typed, evidence-bound contracts for reflective answers."""

from pydantic import BaseModel, ConfigDict, Field

from src.embeddings.contracts import SimilarClaim


class ReflectionModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class ClaimRelation(ReflectionModel):
    source_claim_id: str
    relation_type: str
    target_id: str
    target_kind: str
    target_text: str | None = None


class ReflectionObservation(ReflectionModel):
    statement: str = Field(min_length=1)
    source_claim_ids: list[str] = Field(min_length=1)


class ReflectionResult(ReflectionModel):
    answer: str = Field(min_length=1)
    observations: list[ReflectionObservation] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)


class ReflectionContext(ReflectionModel):
    question: str = Field(min_length=1)
    claims: list[SimilarClaim]
    relations: list[ClaimRelation]
