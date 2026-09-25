from src.services.document_store import Document, DocumentStore
class ListDocuments:
    def __init__(self, documents: DocumentStore): self._documents = documents
    def execute(self) -> list[Document]: return self._documents.list()
