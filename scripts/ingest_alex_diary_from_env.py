#!/usr/bin/env python3
"""Load Alex diary fixtures using credentials supplied through environment variables."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.error import HTTPError

from ingest_alex_diary import format_http_error, load_fixtures, login, request_json


API_URL = os.environ.get("ECHOMIND_API_URL", "http://localhost:8080/api").rstrip("/")


def main() -> int:
    username = os.environ.get("ECHOMIND_AUTH_USERNAME")
    password = os.environ.get("ECHOMIND_AUTH_PASSWORD")
    if not username or not password:
        print("ECHOMIND_AUTH_USERNAME and ECHOMIND_AUTH_PASSWORD are required", file=sys.stderr)
        return 2

    try:
        cookie = login(API_URL, username, password)
    except Exception as error:
        print(f"Authentication failed: {format_http_error(error)}", file=sys.stderr)
        return 1

    loaded = 0
    skipped = 0
    for path, payload in load_fixtures(Path("data/fixtures/alex-diary"), "baseline"):
        note_number = payload["metadata"]["note_number"]
        try:
            status, _, _ = request_json(f"{API_URL}/documents", payload, cookie)
        except HTTPError as error:
            if error.code != 409:
                print(f"FAILED {note_number}: {format_http_error(error)}", file=sys.stderr)
                return 1
            print(f"SKIPPED {note_number}: already exists", flush=True)
            skipped += 1
            continue

        print(f"LOADED {note_number}: HTTP {status}", flush=True)
        loaded += 1

    print(f"Completed: {loaded} loaded, {skipped} skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
