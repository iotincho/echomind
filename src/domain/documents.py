"""Document models independent from HTTP, storage, and extraction."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NewDocument(BaseModel):
    """Information required to register original user material."""

    model_config = ConfigDict(frozen=True)

    content: str
    source: str = Field(default="api", min_length=1, max_length=100)
    metadata: dict[str, str] = Field(default_factory=dict)
    created_at: datetime | None = None
    id: UUID | None = None

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("content must not be blank")
        return value

    @field_validator("created_at")
    @classmethod
    def created_at_must_include_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("created_at must include a timezone")
        return value


class Document(BaseModel):
    """Original material with its stable identity and provenance."""

    model_config = ConfigDict(frozen=True)

    id: UUID
    content: str
    source: str
    metadata: dict[str, str]
    created_at: datetime


def build_document(new_document: NewDocument) -> Document:
    """Assign server defaults without changing supplied source material."""
    return Document(
        id=new_document.id or uuid4(),
        content=new_document.content,
        source=new_document.source,
        metadata=new_document.metadata,
        created_at=new_document.created_at or datetime.now(UTC),
    )
