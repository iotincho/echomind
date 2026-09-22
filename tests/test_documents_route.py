import httpx
import pytest

from app.dependencies import get_ingest_document
from app.main import app
from app.services.document_store import FileDocumentStore
from app.use_cases.ingest_document import IngestDocument


@pytest.mark.anyio
async def test_create_document_delegates_to_use_case_and_returns_created_document(tmp_path) -> None:
    async def override_ingest_document() -> IngestDocument:
        return IngestDocument(FileDocumentStore(tmp_path))

    app.dependency_overrides[get_ingest_document] = override_ingest_document

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
    assert body["content"] == "Estoy evaluando un cambio."
    assert body["source"] == "manual"
    assert (tmp_path / f"{body['id']}.json").is_file()


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
