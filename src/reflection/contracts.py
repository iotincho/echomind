"""Typed, evidence-bound contracts for reflective answers."""

from datetime import datetime

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


class MetadataFieldDefinition(ReflectionModel):
    """Human-readable meaning of a document context field sent to the model."""

    description: str
    value_type: str


class ReflectionDocument(ReflectionModel):
    """Full provenance and metadata for a document represented by retrieved claims."""

    id: str
    source: str | None = None
    created_at: datetime | None = None
    authored_at: datetime | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


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
    documents: list[ReflectionDocument] = Field(default_factory=list)
    metadata_definitions: dict[str, MetadataFieldDefinition] = Field(default_factory=dict)
