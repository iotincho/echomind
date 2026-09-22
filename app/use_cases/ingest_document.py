"""Register original material before any interpretation is performed."""

from app.domain.documents import Document, NewDocument, build_document
from app.services.document_store import DocumentStore


class IngestDocument:
    """Create and persist one source document through the storage port."""

    def __init__(self, document_store: DocumentStore) -> None:
        self._document_store = document_store

    def execute(self, new_document: NewDocument) -> Document:
        document = build_document(new_document)
        self._document_store.save(document)
        return document
