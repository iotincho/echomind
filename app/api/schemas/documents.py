"""HTTP contracts for document ingestion."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.documents import NewDocument


class CreateDocumentRequest(NewDocument):
    """HTTP alias for the application input contract."""


class DocumentResponse(BaseModel):
    id: UUID
    content: str
    source: str
    metadata: dict[str, str]
    created_at: datetime
