"""Provider-neutral models for claim embeddings and semantic retrieval."""

import hashlib
from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class EmbeddingModel(BaseModel):
    """Shared immutable base for embedding contracts."""

    model_config = ConfigDict(frozen=True)


class EmbeddingSpec(EmbeddingModel):
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    dimensions: int = Field(gt=0)

    @property
    def index_suffix(self) -> str:
        value = f"{self.provider}:{self.model}:{self.dimensions}".encode()
        return hashlib.sha256(value).hexdigest()[:16]


class EmbeddingVector(EmbeddingModel):
    vector: list[float] = Field(min_length=1)
    spec: EmbeddingSpec
    input_tokens: int | None = Field(default=None, ge=0)


class ClaimEmbeddingRecord(EmbeddingModel):
    id: str = Field(min_length=1)
    claim_graph_id: str = Field(min_length=1)
    claim_local_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    profile_name: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)
    text_hash: str = Field(min_length=1)
    vector: list[float] = Field(min_length=1)
    spec: EmbeddingSpec
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EvidenceReference(EmbeddingModel):
    quote: str
    start_line: int | None = None
    end_line: int | None = None


class SimilarClaim(EmbeddingModel):
    claim_id: str
    claim_local_id: str
    document_id: str
    run_id: str
    profile_name: str
    prompt_version: str
    text: str
    type: str
    score: float
    evidence: list[EvidenceReference]
    target: Literal["claim"] = "claim"


class DocumentEmbeddingRecord(EmbeddingModel):
    """A versioned vector for the original document, independent of extraction output."""

    id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    text_hash: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source: str = Field(min_length=1)
    metadata: dict[str, str]
    created_at: datetime
    vector: list[float] = Field(min_length=1)
    spec: EmbeddingSpec


class SimilarDocument(EmbeddingModel):
    document_id: str
    content: str
    source: str
    metadata: dict[str, str]
    created_at: datetime
    score: float
    target: Literal["document"] = "document"


SearchResult = Annotated[SimilarClaim | SimilarDocument, Field(discriminator="target")]
