#!/usr/bin/env python3
"""Re-run one stored document through extraction and embeddings without re-uploading it."""

from __future__ import annotations

import argparse
import os
import sys
from urllib.error import HTTPError, URLError

from ingest_alex_diary import format_http_error, login, request_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document_id")
    parser.add_argument("--profile", default="v4")
    parser.add_argument(
        "--api-url",
        default=os.environ.get("ECHOMIND_API_URL", "http://localhost:8080/api"),
    )
    args = parser.parse_args()
    username = os.environ.get("ECHOMIND_AUTH_USERNAME")
    password = os.environ.get("ECHOMIND_AUTH_PASSWORD")
    if not username or not password:
        print("ECHOMIND_AUTH_USERNAME and ECHOMIND_AUTH_PASSWORD are required", file=sys.stderr)
        return 2

    try:
        cookie = login(args.api_url.rstrip("/"), username, password)
        status, _, _ = request_json(
            f"{args.api_url.rstrip('/')}/documents/{args.document_id}/extractions",
            {"profile": args.profile},
            cookie,
        )
    except (HTTPError, URLError, TimeoutError) as error:
        print(f"Reprocessing failed: {format_http_error(error)}", file=sys.stderr)
        return 1

    print(f"REPROCESSED {args.document_id}: HTTP {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
