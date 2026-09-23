from datetime import UTC, datetime
from uuid import uuid4

from app.domain.documents import Document
from app.embeddings.contracts import EmbeddingSpec
from app.extraction.contracts import (
    Claim,
    ClaimType,
    Concept,
    Evidence,
    ExtractionReference,
    ExtractionResult,
    Relationship,
    RelationshipType,
)
from app.graph.neo4j_store import Neo4jGraphStore
from app.services.extraction_store import new_extraction_run


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
    assert len(driver.session_instance.schema_queries) == 7


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
