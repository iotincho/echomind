import httpx
import pytest

from app.dependencies import get_ingest_and_extract_document, get_ingest_document_file
from app.domain.documents import Document
from app.extraction.contracts import Concept, Evidence, ExtractionResult
from app.main import app
from app.services.document_store import FileDocumentStore
from app.services.extraction_store import FileExtractionStore
from app.services.structured_extractor import ProviderExtraction, TokenUsage
from app.use_cases.extract_document import ExtractDocument
from app.use_cases.ingest_and_extract_document import IngestAndExtractDocument
from app.use_cases.ingest_document import IngestDocument
from app.use_cases.ingest_document_file import IngestDocumentFile


class FakeExtractor:
    provider_name = "fake"
    model_name = "fake-model"

    def extract(self, document: Document, profile) -> ProviderExtraction:
        quote = "autonomía" if "autonomía" in document.content else document.content
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


def processing_use_case(tmp_path) -> IngestAndExtractDocument:
    document_store = FileDocumentStore(tmp_path / "documents")
    return IngestAndExtractDocument(
        ingest_document=IngestDocument(document_store),
        extract_document=ExtractDocument(
            document_store,
            FileExtractionStore(tmp_path / "extractions"),
            FakeExtractor(),
        ),
    )


@pytest.mark.anyio
async def test_create_document_delegates_to_use_case_and_returns_created_document(tmp_path) -> None:
    async def override_process_document() -> IngestAndExtractDocument:
        return processing_use_case(tmp_path)

    app.dependency_overrides[get_ingest_and_extract_document] = override_process_document

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/documents",
                json={"content": "Estoy evaluando un cambio.", "source": "manual"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["document"]["content"] == "Estoy evaluando un cambio."
    assert body["document"]["source"] == "manual"
    assert body["extraction"]["status"] == "completed"
    assert (tmp_path / "documents" / f"{body['document']['id']}.json").is_file()


@pytest.mark.anyio
async def test_create_document_from_markdown_file(tmp_path) -> None:
    async def override_ingest_document_file() -> IngestDocumentFile:
        return IngestDocumentFile(FileDocumentStore(tmp_path / "documents"))

    async def override_process_document() -> IngestAndExtractDocument:
        return processing_use_case(tmp_path)

    app.dependency_overrides[get_ingest_document_file] = override_ingest_document_file
    app.dependency_overrides[get_ingest_and_extract_document] = override_process_document

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/documents/files",
                files={
                    "file": (
                        "reflexion.md",
                        b"# Una nota\n\nContenido original",
                        "text/markdown",
                    )
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["document"]["metadata"] == {"filename": "reflexion.md", "format": "md"}
    assert response.json()["extraction"]["status"] == "completed"
    assert (tmp_path / "documents" / f"{response.json()['document']['id']}.json").is_file()


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
