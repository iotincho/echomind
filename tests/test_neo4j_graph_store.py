from datetime import UTC, datetime
from uuid import uuid4

from src.domain.documents import Document
from src.embeddings.contracts import EmbeddingSpec
from src.extraction.contracts import (
    Claim,
    ClaimType,
    Concept,
    Evidence,
    ExtractionReference,
    ExtractionResult,
    Relationship,
    RelationshipType,
)
from src.graph.neo4j_store import Neo4jGraphStore
from src.services.extraction_store import new_extraction_run


class FakeResult:
    def __init__(self, records: list["FakeRecord"] | None = None) -> None:
        self._records = records or []

    def consume(self) -> None:
        return None

    def single(self) -> dict[str, int]:
        return {"persisted_count": 1}

    def __iter__(self):
        return iter(self._records)


class FakeRecord:
    def __init__(self, values: dict) -> None:
        self._values = values

    def data(self) -> dict:
        return self._values


class FakeTransaction:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def run(self, query: str, **parameters) -> FakeResult:
        self.calls.append((query, parameters))
        return FakeResult()


class FakeSession:
    def __init__(self) -> None:
        self.schema_queries: list[str] = []
        self.transaction = FakeTransaction()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def run(self, query: str, **_parameters) -> FakeResult:
        self.schema_queries.append(query)
        return FakeResult()

    def execute_write(self, function, *arguments) -> None:
        function(self.transaction, *arguments)


class FakeDriver:
    def __init__(self) -> None:
        self.session_instance = FakeSession()

    def session(self) -> FakeSession:
        return self.session_instance

    def close(self) -> None:
        return None


def test_neo4j_graph_store_persists_items_relationships_and_evidence() -> None:
    document = Document(
        id=uuid4(),
        content="Quiero más autonomía.",
        source="test",
        metadata={"filename": "note.md"},
        created_at=datetime.now(UTC),
    )
    evidence = Evidence(
        quote="autonomía",
        start_char=11,
        end_char=20,
        start_line=1,
        end_line=1,
    )
    result = ExtractionResult(
        concepts=[Concept(id="autonomy", name="autonomía", evidence=[evidence])],
        entities=[],
        claims=[
            Claim(
                id="claim_1",
                text="Quiero más autonomía.",
                type=ClaimType.DESIRE,
                evidence=[evidence],
            )
        ],
        relationships=[
            Relationship(
                source=ExtractionReference(kind="claim", id="claim_1"),
                type=RelationshipType.ABOUT,
                target=ExtractionReference(kind="concept", id="autonomy"),
                evidence=[evidence],
            )
        ],
    )
    run = new_extraction_run(
        document_id=document.id,
        profile_name="v3",
        schema_version="v2",
        prompt_version="v3",
        provider="fake",
        model="fake-model",
        status="completed",
        result=result,
    )
    driver = FakeDriver()

    Neo4jGraphStore("bolt://graph:7687", "neo4j", "password", driver=driver).persist(document, run)

    queries = "\n".join(query for query, _ in driver.session_instance.transaction.calls)
    assert "MERGE (document:Document" in queries
    assert "MERGE (item:Concept" in queries
    assert "MERGE (item:Claim" in queries
    assert "relationship:ABOUT" in queries
    assert "MERGE (evidence:Evidence" in queries
    assert len(driver.session_instance.schema_queries) == 8


def test_neo4j_graph_store_search_keeps_run_in_cypher_scope() -> None:
    class SearchSession(FakeSession):
        def run(self, query: str, **parameters) -> FakeResult:
            self.schema_queries.append(query)
            if "db.index.vector.queryNodes" not in query:
                return FakeResult()
            assert parameters["index_name"] == "claim_embedding_6b9a3a1fa395f70b"
            return FakeResult(
                [
                    FakeRecord(
                        {
                            "claim_id": "run:claim:claim_1",
                            "claim_local_id": "claim_1",
                            "document_id": "document",
                            "run_id": "run",
                            "profile_name": "v3",
                            "prompt_version": "v3",
                            "text": "Quiero más autonomía.",
                            "type": "desire",
                            "score": 0.9,
                            "evidence": [],
                        }
                    )
                ]
            )

    class SearchDriver(FakeDriver):
        def __init__(self) -> None:
            self.session_instance = SearchSession()

    spec = EmbeddingSpec(provider="openai", model="text-embedding-3-small", dimensions=1536)
    results = Neo4jGraphStore(
        "bolt://graph:7687", "neo4j", "password", driver=SearchDriver()
    ).search_claim_embeddings([0.0] * 1536, spec, limit=10)

    assert results[0].profile_name == "v3"


def test_neo4j_graph_store_persists_and_searches_document_embeddings() -> None:
    from src.embeddings.contracts import DocumentEmbeddingRecord

    class DocumentSearchSession(FakeSession):
        def run(self, query: str, **parameters) -> FakeResult:
            self.schema_queries.append(query)
            if "db.index.vector.queryNodes" not in query:
                return FakeResult()
            assert parameters["index_name"] == "document_embedding_6b9a3a1fa395f70b"
            return FakeResult(
                [
                    FakeRecord(
                        {
                            "document_id": "document",
                            "content": "Quiero más autonomía.",
                            "source": "test",
                            "metadata_json": '{"filename": "note.md"}',
                            "created_at": "2026-01-01T00:00:00+00:00",
                            "score": 0.9,
                        }
                    )
                ]
            )

    class DocumentSearchDriver(FakeDriver):
        def __init__(self) -> None:
            self.session_instance = DocumentSearchSession()

    spec = EmbeddingSpec(provider="openai", model="text-embedding-3-small", dimensions=1536)
    driver = DocumentSearchDriver()
    store = Neo4jGraphStore("bolt://graph:7687", "neo4j", "password", driver=driver)
    record = DocumentEmbeddingRecord(
        id="document:embedding:6b9a3a1fa395f70b:hash",
        document_id="document",
        text_hash="hash",
        content="Quiero más autonomía.",
        source="test",
        metadata={"filename": "note.md"},
        created_at=datetime.now(UTC),
        vector=[0.0] * 1536,
        spec=spec,
    )

    store.persist_document_embedding(record, spec)
    results = store.search_document_embeddings([0.0] * 1536, spec, limit=10)

    writes = "\n".join(query for query, _ in driver.session_instance.transaction.calls)
    assert "MERGE (embedding:DocumentEmbedding" in writes
    assert "MATCH (document:Document" in writes
    assert results[0].target == "document"
    assert results[0].metadata == {"filename": "note.md"}


def test_neo4j_graph_store_persists_claim_embeddings_without_binding_self() -> None:
    from src.embeddings.contracts import ClaimEmbeddingRecord

    spec = EmbeddingSpec(provider="openai", model="text-embedding-3-small", dimensions=1536)
    driver = FakeDriver()
    store = Neo4jGraphStore("bolt://graph:7687", "neo4j", "password", driver=driver)
    store.persist_claim_embeddings(
        [
            ClaimEmbeddingRecord(
                id="claim:embedding",
                claim_graph_id="run:claim:claim",
                claim_local_id="claim",
                document_id="document",
                run_id="run",
                profile_name="v3",
                prompt_version="v3",
                text_hash="hash",
                vector=[0.0] * 1536,
                spec=spec,
            )
        ],
        spec,
    )

    writes = "\n".join(query for query, _ in driver.session_instance.transaction.calls)
    assert "MERGE (embedding:ClaimEmbedding" in writes
