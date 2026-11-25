#!/usr/bin/env python3
"""
Task 1 (Load Raw): Load raw JSON pages into DuckDB raw_api_orders idempotently.

Reads data/raw/<YYYY-MM-DD>/page_*.json and replaces only that batch_date's rows
inside a single DuckDB transaction so re-running the same date never duplicates data.
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

import duckdb


AP2_ROOT = Path(__file__).resolve().parent.parent


def _page_sort_key(path: Path) -> int:
    match = re.search(r"page_(\d+)\.json$", path.name)
    return int(match.group(1)) if match else 0


def load_raw_for_date(
    batch_date: str,
    db_path: Path = AP2_ROOT / "northmart.duckdb",
    raw_dir: Path = AP2_ROOT / "data" / "raw",
) -> int:
    """Load landed JSON files for batch_date into DuckDB raw_api_orders."""
    date_dir = raw_dir / batch_date
    page_files = sorted(date_dir.glob("page_*.json"), key=_page_sort_key)
    if not page_files:
        raise FileNotFoundError(f"No raw JSON pages found in {date_dir}")

    ingested_at = datetime.now(timezone.utc).replace(tzinfo=None)
    rows = []

    for page_file in page_files:
        payload = json.loads(page_file.read_text(encoding="utf-8"))
        page_num = int(payload["page"])
        for item in payload.get("items", []):
            rows.append(
                (
                    batch_date,
                    page_num,
                    item.get("order_id"),
                    item.get("order_item_id"),
                    item.get("customer_id"),
                    item.get("product_id"),
                    item.get("seller_id"),
                    item.get("order_status"),
                    item.get("order_purchase_timestamp"),
                    item.get("price"),
                    item.get("freight_value"),
                    ingested_at,
                )
            )

    con = duckdb.connect(str(db_path))
    try:
        con.execute("BEGIN TRANSACTION;")
        con.execute(
            "DELETE FROM raw_api_orders WHERE batch_date = CAST(? AS DATE);",
            [batch_date],
        )
        if rows:
            con.executemany(
                """
                INSERT INTO raw_api_orders (
                    batch_date,
                    page,
                    order_id,
                    order_item_id,
                    customer_id,
                    product_id,
                    seller_id,
                    order_status,
                    order_purchase_timestamp,
                    price,
                    freight_value,
                    ingested_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
        con.execute("COMMIT;")
    except Exception:
        con.execute("ROLLBACK;")
        raise
    finally:
        con.close()

    print(
        f"[LOAD RAW DONE] date={batch_date} files={len(page_files)} rows_loaded={len(rows)}"
    )
    return len(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load raw JSON pages into DuckDB.")
    parser.add_argument("--date", required=True, help="Execution date (YYYY-MM-DD).")
    parser.add_argument(
        "--db",
        type=Path,
        default=AP2_ROOT / "northmart.duckdb",
        help="Path to DuckDB database.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=AP2_ROOT / "data" / "raw",
        help="Raw landing directory.",
    )
    args = parser.parse_args()
    load_raw_for_date(args.date, db_path=args.db, raw_dir=args.raw_dir)

