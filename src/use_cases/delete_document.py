from uuid import UUID
from src.services.document_store import DocumentStore
from src.services.extraction_store import ExtractionStore
from src.graph.neo4j_store import Neo4jGraphStore
class DeleteDocument:
    def __init__(self, documents: DocumentStore, extractions: ExtractionStore, graph: Neo4jGraphStore): self._documents=documents; self._extractions=extractions; self._graph=graph
    def execute(self, document_id: UUID) -> None:
        self._documents.get(document_id)
        self._graph.delete_document(str(document_id))
        self._extractions.delete_for_document(document_id)
        self._documents.delete(document_id)
