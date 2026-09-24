"""Contract tests for the reproducible synthetic EchoMind evaluation corpus."""

import json
from datetime import UTC
from pathlib import Path

from src.domain.documents import NewDocument

FIXTURES_DIRECTORY = Path("data/fixtures/alex-diary")


def test_alex_diary_fixtures_are_valid_new_documents_in_temporal_order() -> None:
    fixtures = sorted(FIXTURES_DIRECTORY.glob("*.json"))

    assert len(fixtures) == 18

    documents = [
        NewDocument.model_validate(json.loads(path.read_text(encoding="utf-8")))
        for path in fixtures
    ]
    assert [document.metadata["note_number"] for document in documents] == [
        f"{number:02}" for number in range(1, 19)
    ]
    assert [document.metadata["phase"] for document in documents] == ["baseline"] * 15 + [
        "incremental"
    ] * 3
    assert all(document.source == "synthetic_fixture" for document in documents)
    assert all(document.created_at is not None for document in documents)
    assert all(
        document.created_at.utcoffset() is not None for document in documents if document.created_at
    )
    assert [
        document.created_at.astimezone(UTC) for document in documents if document.created_at
    ] == sorted(
        document.created_at.astimezone(UTC) for document in documents if document.created_at
    )
