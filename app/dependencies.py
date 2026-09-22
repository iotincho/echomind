"""Composition root for infrastructure adapters and application use cases."""

from functools import lru_cache

from app.config import get_settings
from app.services.document_store import FileDocumentStore
from app.use_cases.ingest_document import IngestDocument


@lru_cache
def get_document_store() -> FileDocumentStore:
    """Provide the local development adapter for original documents."""
    return FileDocumentStore(get_settings().documents_path)


async def get_ingest_document() -> IngestDocument:
    """Build the application operation used by any delivery interface."""
    return IngestDocument(get_document_store())
