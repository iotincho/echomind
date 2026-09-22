"""Durable storage port and local filesystem adapter for Documents."""

import json
from pathlib import Path
from typing import Protocol

from app.domain.documents import Document


class DocumentAlreadyExistsError(Exception):
    """Raised when a caller retries with an already persisted stable ID."""


class DocumentStore(Protocol):
    """Persistence boundary used by document use cases."""

    def save(self, document: Document) -> None:
        """Persist one original document."""


class FileDocumentStore:
    """Store each original document in a separate, auditable JSON file."""

    def __init__(self, directory: Path) -> None:
        self._directory = directory

    def save(self, document: Document) -> None:
        self._directory.mkdir(parents=True, exist_ok=True)
        destination = self._directory / f"{document.id}.json"
        if destination.exists():
            raise DocumentAlreadyExistsError(f"Document {document.id} already exists")

        temporary = destination.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(document.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(destination)
