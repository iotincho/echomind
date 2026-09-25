"""Tests for the local Alex diary API loader."""

import importlib.util
from pathlib import Path

SCRIPT_PATH = Path("scripts/ingest_alex_diary.py")
SPEC = importlib.util.spec_from_file_location("ingest_alex_diary", SCRIPT_PATH)
assert SPEC and SPEC.loader
ingest_alex_diary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ingest_alex_diary)


def test_load_fixtures_selects_the_baseline_in_note_order() -> None:
    fixtures = ingest_alex_diary.load_fixtures(
        Path("data/fixtures/alex-diary"),
        "baseline",
    )

    assert len(fixtures) == 15
    assert [payload["metadata"]["note_number"] for _, payload in fixtures] == [
        f"{number:02}" for number in range(1, 16)
    ]
    assert all(payload["authored_at"].endswith("-03:00") for _, payload in fixtures)


def test_load_fixtures_selects_only_the_incremental_notes() -> None:
    fixtures = ingest_alex_diary.load_fixtures(
        Path("data/fixtures/alex-diary"),
        "incremental",
    )

    assert [payload["metadata"]["note_number"] for _, payload in fixtures] == ["16", "17", "18"]
