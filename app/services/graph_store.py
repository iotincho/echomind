"""Port for persisting validated extractions in a knowledge graph."""

from typing import Protocol

from app.domain.documents import Document
from app.services.extraction_store import ExtractionRun


class GraphPersistenceError(RuntimeError):
    """Raised when a completed extraction cannot be stored in the graph."""


class GraphStore(Protocol):
    """Infrastructure boundary shared by application use cases and delivery adapters."""

    def persist(self, document: Document, extraction: ExtractionRun) -> None:
        """Write one completed, evidence-backed extraction atomically."""
