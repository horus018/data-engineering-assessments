#!/usr/bin/env python3
"""
Task 1 (Extract): Fetch daily order items from the NorthMart Mock REST API.

Handles:
  - Pagination (page=1 .. total_pages)
  - Transient HTTP 503 errors with exponential backoff retries
  - Landing the exact raw HTTP JSON response unchanged into data/raw/<YYYY-MM-DD>/
"""

import argparse
from datetime import date as Date
import os
from pathlib import Path
import shutil
import time

import requests


AP2_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_API_URL = os.environ.get("NORTHMART_API_URL", "http://localhost:8000")
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def _fetch_page_with_retries(
    session: requests.Session,
    api_url: str,
    batch_date: str,
    page: int,
    max_retries: int = 6,
    base_delay: float = 0.5,
) -> tuple[bytes, dict]:
    """Fetch one API page, retrying transient HTTP 503 and network errors."""
    endpoint = f"{api_url.rstrip('/')}/orders"
    params = {"date": batch_date, "page": page}

    for attempt in range(1, max_retries + 1):
        try:
            response = session.get(endpoint, params=params, timeout=10)
            if response.status_code == 200:
                return response.content, response.json()

            if response.status_code in RETRYABLE_STATUS_CODES:
                delay = base_delay * (2 ** (attempt - 1))
                print(
                    f"[RETRY {attempt}/{max_retries}] date={batch_date} page={page} "
                    f"HTTP {response.status_code} - sleeping {delay:.2f}s"
                )
                time.sleep(delay)
                continue

            raise RuntimeError(
                f"Non-retryable API error HTTP {response.status_code} for "
                f"date={batch_date} page={page}: {response.text}"
            )
        except requests.RequestException as exc:
            if attempt == max_retries:
                raise RuntimeError(
                    f"Request failed after {max_retries} attempts for "
                    f"date={batch_date} page={page}: {exc}"
                ) from exc
            delay = base_delay * (2 ** (attempt - 1))
            print(
                f"[RETRY {attempt}/{max_retries}] date={batch_date} page={page} "
                f"network error ({exc}) - sleeping {delay:.2f}s"
            )
            time.sleep(delay)

    raise RuntimeError(f"Exhausted {max_retries} retries for date={batch_date} page={page}")


def extract_orders_for_date(
    batch_date: str,
    api_url: str = DEFAULT_API_URL,
    raw_dir: Path = AP2_ROOT / "data" / "raw",
    max_retries: int = 6,
) -> int:
    """Download all pages for one execution date and save raw JSON files."""
    Date.fromisoformat(batch_date)  # Validates YYYY-MM-DD format

    date_dir = raw_dir / batch_date
    if date_dir.exists():
        shutil.rmtree(date_dir)
    date_dir.mkdir(parents=True, exist_ok=True)

    total_items = 0
    page = 1
    total_pages = 1

    with requests.Session() as session:
        while page <= total_pages:
            raw_bytes, payload = _fetch_page_with_retries(
                session=session,
                api_url=api_url,
                batch_date=batch_date,
                page=page,
                max_retries=max_retries,
            )
            total_pages = int(payload["total_pages"])
            items = payload.get("items", [])
            total_items += len(items)

            out_file = date_dir / f"page_{page}.json"
            out_file.write_bytes(raw_bytes)
            print(
                f"[EXTRACT] date={batch_date} page={page}/{total_pages} "
                f"items={len(items)} -> {out_file}"
            )
            page += 1

    print(
        f"[EXTRACT DONE] date={batch_date} pages={total_pages} total_items={total_items}"
    )
    return total_items


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract NorthMart orders for a date.")
    parser.add_argument("--date", required=True, help="Execution date (YYYY-MM-DD).")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="Base URL of Mock API.")
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=AP2_ROOT / "data" / "raw",
        help="Raw landing directory.",
    )
    args = parser.parse_args()
    extract_orders_for_date(args.date, api_url=args.api_url, raw_dir=args.raw_dir)

