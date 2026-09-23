from datetime import UTC, datetime
from uuid import uuid4

import httpx
import pytest

from app.dependencies import get_extract_persist_and_embed_document
from app.domain.documents import Document
from app.embeddings.contracts import EmbeddingSpec, EmbeddingVector
from app.extraction.contracts import Concept, Evidence, ExtractionResult
from app.main import app
from app.services.document_store import FileDocumentStore
from app.services.embedding_provider import EmbeddingProvider
from app.services.extraction_store import FileExtractionStore
from app.services.graph_store import GraphStore
from app.services.structured_extractor import ProviderExtraction, TokenUsage
from app.use_cases.embed_claims import EmbedClaims
from app.use_cases.extract_and_persist_document import ExtractAndPersistDocument
from app.use_cases.extract_document import ExtractDocument
from app.use_cases.extract_persist_and_embed_document import ExtractPersistAndEmbedDocument


class FakeExtractor:
    provider_name = "fake"
    model_name = "fake-model"

    def extract(self, document: Document, profile) -> ProviderExtraction:
        quote = "autonomía"
        start = document.content.index(quote)
        return ProviderExtraction(
            result=ExtractionResult(
                concepts=[
                    Concept(
                        id="concept_1",
                        name=quote,
                        evidence=[
                            Evidence(start_char=start, end_char=start + len(quote), quote=quote)
                        ],
                    )
                ],
                entities=[],
                claims=[],
                relationships=[],
            ),
            provider=self.provider_name,
            model=self.model_name,
            usage=TokenUsage(),
        )


class FakeGraphStore(GraphStore):
    def __init__(self) -> None:
        self.persisted: list[tuple[Document, object]] = []

    def persist(self, document: Document, extraction: object) -> None:
        self.persisted.append((document, extraction))

    def persist_claim_embeddings(self, records, spec) -> None:
        return None

    def search_claim_embeddings(self, vector, spec, limit):
        return []


class FakeEmbeddingProvider(EmbeddingProvider):
    spec = EmbeddingSpec(provider="fake", model="fake-model", dimensions=2)

    def embed(self, texts: list[str]) -> list[EmbeddingVector]:
        return [EmbeddingVector(vector=[0.1, 0.2], spec=self.spec) for _ in texts]


@pytest.mark.anyio
async def test_create_extraction_persists_the_completed_run_in_the_graph(tmp_path) -> None:
    document = Document(
        id=uuid4(),
        content="Quiero más autonomía.",
        source="test",
        metadata={},
        created_at=datetime.now(UTC),
    )
    document_store = FileDocumentStore(tmp_path / "documents")
    document_store.save(document)

    graph_store = FakeGraphStore()

    async def override_extract_persist_and_embed_document() -> ExtractPersistAndEmbedDocument:
        return ExtractPersistAndEmbedDocument(
            ExtractAndPersistDocument(
                ExtractDocument(
                    document_store,
                    FileExtractionStore(tmp_path / "extractions"),
                    FakeExtractor(),
                ),
                graph_store,
            ),
            EmbedClaims(FakeEmbeddingProvider(), graph_store),
        )

    app.dependency_overrides[get_extract_persist_and_embed_document] = (
        override_extract_persist_and_embed_document
    )
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/documents/{document.id}/extractions",
                json={"profile": "v1"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["status"] == "completed"
    assert response.json()["result"]["concepts"][0]["name"] == "autonomía"
    assert graph_store.persisted[0][0].id == document.id


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
