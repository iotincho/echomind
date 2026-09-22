from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain.documents import NewDocument
from app.services.document_store import DocumentAlreadyExistsError, FileDocumentStore
from app.use_cases.ingest_document import IngestDocument
from app.use_cases.ingest_document_file import (
    IngestDocumentFile,
    InvalidDocumentEncodingError,
    UnsupportedDocumentFileError,
)


def test_ingest_document_preserves_original_content_and_metadata(tmp_path) -> None:
    document_id = uuid4()
    created_at = datetime(2026, 9, 22, 12, 0, tzinfo=UTC)
    use_case = IngestDocument(FileDocumentStore(tmp_path))

    document = use_case.execute(
        NewDocument(
            id=document_id,
            content="Quiero más autonomía en mi trabajo.",
            source="manual",
            created_at=created_at,
        )
    )

    assert document.id == document_id
    assert document.content == "Quiero más autonomía en mi trabajo."
    assert document.created_at == created_at
    assert (tmp_path / f"{document_id}.json").is_file()


def test_ingest_document_rejects_repeated_stable_id(tmp_path) -> None:
    use_case = IngestDocument(FileDocumentStore(tmp_path))
    document = NewDocument(id=uuid4(), content="Nota original")
    use_case.execute(document)

    with pytest.raises(DocumentAlreadyExistsError):
        use_case.execute(document)


def test_ingest_document_file_preserves_filename_and_format(tmp_path) -> None:
    use_case = IngestDocumentFile(FileDocumentStore(tmp_path))

    document = use_case.execute("reflexion.md", b"# Nota\n\nQuiero cambiar de trabajo.")

    assert document.content == "# Nota\n\nQuiero cambiar de trabajo."
    assert document.source == "file_upload"
    assert document.metadata == {"filename": "reflexion.md", "format": "md"}


@pytest.mark.parametrize(
    ("filename", "content", "error"),
    [
        ("imagen.pdf", b"not a PDF", UnsupportedDocumentFileError),
        ("nota.txt", b"\xff\xfe", InvalidDocumentEncodingError),
    ],
)
def test_ingest_document_file_rejects_unsupported_input(tmp_path, filename, content, error) -> None:
    use_case = IngestDocumentFile(FileDocumentStore(tmp_path))

    with pytest.raises(error):
        use_case.execute(filename, content)
