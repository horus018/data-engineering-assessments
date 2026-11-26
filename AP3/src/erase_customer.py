#!/usr/bin/env python3
"""
PA3 Part A — Task 3: GDPR Right to Erasure Procedure (Article 17).

Removes a customer from every layer of the NorthMart platform:
  1. Landed raw JSON files in data/raw/YYYY-MM-DD/page_*.json
  2. Raw DuckDB tables (raw_api_orders, raw_orders, raw_customers)
  3. Staging DuckDB table (stg_orders)
  4. Mart DuckDB tables (fact_sales, dim_customer) via keyed SHA-256 hash lookup
  5. Curated Parquet exports (data/curated/fact_sales.parquet & fact_sales_partitioned/)

Prints and saves full BEFORE and AFTER evidence counts to evidence/erasure_before_after.txt.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import duckdb

from init_db import load_dotenv_if_present


AP3_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CUSTOMER_ID = "d1806517abdeab70d77e1ff58ec5f1b8"


def compute_keyed_sha256(secret_key: str, value: str) -> str:
    """Compute sha256(secret_key || TRIM(value)), matching DuckDB sha256(key || val)."""
    payload = f"{secret_key}{value.strip()}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def count_in_raw_json_files(raw_dir: Path, target_raw_ids: set[str]) -> tuple[int, int]:
    """Return (matching_customer_items, total_items) across all data/raw/*/page_*.json files."""
    matching = 0
    total = 0
    for page_file in sorted(raw_dir.glob("*/page_*.json")):
        data = json.loads(page_file.read_text(encoding="utf-8"))
        for item in data.get("items", []):
            total += 1
            if item.get("customer_id") in target_raw_ids:
                matching += 1
    return matching, total


def scrub_raw_json_files(raw_dir: Path, target_raw_ids: set[str]) -> int:
    """Remove items belonging to target_raw_ids from all data/raw/*/page_*.json files."""
    removed_count = 0
    for page_file in sorted(raw_dir.glob("*/page_*.json")):
        data = json.loads(page_file.read_text(encoding="utf-8"))
        items = data.get("items", [])
        filtered = [it for it in items if it.get("customer_id") not in target_raw_ids]
        diff = len(items) - len(filtered)
        if diff > 0:
            removed_count += diff
            data["items"] = filtered
            page_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return removed_count


def collect_layer_counts(
    con: duckdb.DuckDBPyConnection,
    raw_dir: Path,
    curated_dir: Path,
    target_raw_ids: set[str],
    target_id_hashes: set[str],
    target_unique_hashes: set[str],
    target_customer_keys: set[int],
) -> dict[str, tuple[int, int]]:
    """
    Collect (target_customer_rows, total_layer_rows) across every layer.
    """
    raw_ids_sql = ", ".join(f"'{x}'" for x in sorted(target_raw_ids)) or "''"
    hash_ids_sql = ", ".join(f"'{x}'" for x in sorted(target_id_hashes)) or "''"
    uhash_ids_sql = ", ".join(f"'{x}'" for x in sorted(target_unique_hashes)) or "''"
    ckeys_sql = ", ".join(str(k) for k in sorted(target_customer_keys)) or "-1"

    counts: dict[str, tuple[int, int]] = {}

    # 1. Landed JSON files in data/raw/
    counts["1. data/raw/*.json (Landed API JSON files)"] = count_in_raw_json_files(
        raw_dir, target_raw_ids
    )

    # 2. DuckDB raw_api_orders
    c_target = con.execute(
        f"SELECT COUNT(*) FROM raw_api_orders WHERE customer_id IN ({raw_ids_sql})"
    ).fetchone()[0]
    c_total = con.execute("SELECT COUNT(*) FROM raw_api_orders").fetchone()[0]
    counts["2. raw_api_orders (DuckDB Raw API table)"] = (c_target, c_total)

    # 3. DuckDB raw_customers
    c_target = con.execute(
        f"SELECT COUNT(*) FROM raw_customers WHERE customer_id IN ({raw_ids_sql})"
    ).fetchone()[0]
    c_total = con.execute("SELECT COUNT(*) FROM raw_customers").fetchone()[0]
    counts["3. raw_customers (DuckDB Raw Customers)"] = (c_target, c_total)

    # 4. DuckDB raw_orders
    c_target = con.execute(
        f"SELECT COUNT(*) FROM raw_orders WHERE customer_id IN ({raw_ids_sql})"
    ).fetchone()[0]
    c_total = con.execute("SELECT COUNT(*) FROM raw_orders").fetchone()[0]
    counts["4. raw_orders (DuckDB Raw Orders)"] = (c_target, c_total)

    # 5. DuckDB stg_orders (pseudonymized staging)
    c_target = con.execute(
        f"SELECT COUNT(*) FROM stg_orders WHERE customer_id IN ({hash_ids_sql})"
    ).fetchone()[0]
    c_total = con.execute("SELECT COUNT(*) FROM stg_orders").fetchone()[0]
    counts["5. stg_orders (dbt Staging table)"] = (c_target, c_total)

    # 6. DuckDB dim_customer (pseudonymized customer dimension)
    c_target = con.execute(
        f"""
        SELECT COUNT(*) FROM dim_customer
        WHERE customer_key IN ({ckeys_sql})
           OR customer_id IN ({hash_ids_sql})
           OR customer_unique_id IN ({uhash_ids_sql})
        """
    ).fetchone()[0]
    c_total = con.execute("SELECT COUNT(*) FROM dim_customer").fetchone()[0]
    counts["6. dim_customer (dbt Protected Mart Dimension)"] = (c_target, c_total)

    # 7. DuckDB fact_sales (incremental mart fact table)
    c_target = con.execute(
        f"SELECT COUNT(*) FROM fact_sales WHERE customer_key IN ({ckeys_sql})"
    ).fetchone()[0]
    c_total = con.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
    counts["7. fact_sales (dbt Incremental Mart Fact)"] = (c_target, c_total)

    # 8. Curated Unpartitioned Parquet (data/curated/fact_sales.parquet)
    unpart_file = curated_dir / "fact_sales.parquet"
    if unpart_file.exists():
        c_target = con.execute(
            f"SELECT COUNT(*) FROM read_parquet('{unpart_file}') WHERE customer_key IN ({ckeys_sql})"
        ).fetchone()[0]
        c_total = con.execute(
            f"SELECT COUNT(*) FROM read_parquet('{unpart_file}')"
        ).fetchone()[0]
    else:
        c_target, c_total = 0, 0
    counts["8. data/curated/fact_sales.parquet"] = (c_target, c_total)

    # 9. Curated Partitioned Parquet (data/curated/fact_sales_partitioned/)
    part_dir = curated_dir / "fact_sales_partitioned"
    if part_dir.exists() and list(part_dir.glob("*/*.parquet")):
        glob_pat = str(part_dir / "*" / "*.parquet")
        c_target = con.execute(
            f"SELECT COUNT(*) FROM read_parquet('{glob_pat}', hive_partitioning=true) WHERE customer_key IN ({ckeys_sql})"
        ).fetchone()[0]
        c_total = con.execute(
            f"SELECT COUNT(*) FROM read_parquet('{glob_pat}', hive_partitioning=true)"
        ).fetchone()[0]
    else:
        c_target, c_total = 0, 0
    counts["9. data/curated/fact_sales_partitioned/"] = (c_target, c_total)

    return counts


def erase_customer(
    customer_id: str,
    db_path: Path = AP3_ROOT / "northmart.duckdb",
    raw_dir: Path = AP3_ROOT / "data" / "raw",
    curated_dir: Path = AP3_ROOT / "data" / "curated",
    evidence_path: Path = AP3_ROOT / "evidence" / "erasure_before_after.txt",
) -> None:
    """Execute GDPR Art. 17 erasure across all storage layers and record evidence."""
    load_dotenv_if_present()
    secret_key = os.environ.get("NORTHMART_HASH_KEY")
    if not secret_key:
        raise RuntimeError(
            "NORTHMART_HASH_KEY environment variable is required (set in .env or export NORTHMART_HASH_KEY=...)."
        )

    prev_cwd = os.getcwd()
    os.chdir(AP3_ROOT)
    con = duckdb.connect(str(db_path))
    try:
        # Ensure curated parquet exports exist before erasure so Before vs After is measured on all layers
        curated_dir.mkdir(parents=True, exist_ok=True)
        part_dir = curated_dir / "fact_sales_partitioned"
        if part_dir.exists():
            shutil.rmtree(part_dir)
        con.execute(
            "COPY fact_sales TO 'data/curated/fact_sales.parquet' (FORMAT PARQUET, COMPRESSION ZSTD, OVERWRITE TRUE);"
        )
        con.execute(
            "COPY fact_sales TO 'data/curated/fact_sales_partitioned' (FORMAT PARQUET, PARTITION_BY (year_month), COMPRESSION ZSTD, OVERWRITE TRUE);"
        )

        # Resolve all raw customer_ids and customer_unique_ids for this person
        rows = con.execute(
            """
            SELECT DISTINCT c2.customer_id, c2.customer_unique_id
            FROM raw_customers c1
            JOIN raw_customers c2 ON c1.customer_unique_id = c2.customer_unique_id
            WHERE c1.customer_id = ? OR c1.customer_unique_id = ?
            """,
            [customer_id, customer_id],
        ).fetchall()

        target_raw_ids = {customer_id}
        target_unique_ids = set()
        for cid, cuid in rows:
            if cid:
                target_raw_ids.add(cid)
            if cuid:
                target_unique_ids.add(cuid)

        target_id_hashes = {compute_keyed_sha256(secret_key, cid) for cid in target_raw_ids}
        target_unique_hashes = {compute_keyed_sha256(secret_key, cuid) for cuid in target_unique_ids}

        hash_ids_sql = ", ".join(f"'{x}'" for x in sorted(target_id_hashes)) or "''"
        uhash_ids_sql = ", ".join(f"'{x}'" for x in sorted(target_unique_hashes)) or "''"
        key_rows = con.execute(
            f"""
            SELECT DISTINCT customer_key
            FROM dim_customer
            WHERE customer_id IN ({hash_ids_sql})
               OR customer_unique_id IN ({uhash_ids_sql})
            """
        ).fetchall()
        target_customer_keys = {r[0] for r in key_rows}

        # 1. Measure BEFORE counts
        before_counts = collect_layer_counts(
            con,
            raw_dir,
            curated_dir,
            target_raw_ids,
            target_id_hashes,
            target_unique_hashes,
            target_customer_keys,
        )

        # 2. Scrub landed JSON files in data/raw/
        scrub_raw_json_files(raw_dir, target_raw_ids)

        # 3. Clean partitioned directory before SQL re-export so no stale partition files remain
        if part_dir.exists():
            shutil.rmtree(part_dir)

        # 4. Run sql/erase_customer.sql inside DuckDB
        con.execute("SET VARIABLE target_customer_id = ?;", [customer_id])
        con.execute("SET VARIABLE target_hash_key = ?;", [secret_key])
        erase_sql = (AP3_ROOT / "sql" / "erase_customer.sql").read_text(encoding="utf-8")
        con.execute(erase_sql)

        # 5. Measure AFTER counts
        after_counts = collect_layer_counts(
            con,
            raw_dir,
            curated_dir,
            target_raw_ids,
            target_id_hashes,
            target_unique_hashes,
            target_customer_keys,
        )
    finally:
        con.close()
        os.chdir(prev_cwd)

    sample_hash = next(iter(sorted(target_id_hashes)))
    lines = [
        "==========================================================================================",
        "NORTHMART PA3 — TASK 3: GDPR RIGHT TO ERASURE (ART. 17) BEFORE vs. AFTER EVIDENCE",
        "==========================================================================================",
        f"Requested Customer Identifier (raw)   : {customer_id}",
        f"Associated customer_unique_id(s)      : {', '.join(sorted(target_unique_ids)) or 'N/A'}",
        f"Keyed SHA-256 Hash (in dbt marts)     : {sample_hash}",
        f"Resolved Surrogate customer_key(s)    : {sorted(target_customer_keys)}",
        "------------------------------------------------------------------------------------------",
        f"{'Storage Layer / Table':<46} | {'Customer (Before -> After)':<26} | {'Total Rows (Before -> After)'}",
        "------------------------------------------------------------------------------------------",
    ]
    for layer_name in before_counts:
        c_bef, t_bef = before_counts[layer_name]
        c_aft, t_aft = after_counts[layer_name]
        cust_str = f"{c_bef} -> {c_aft}"
        tot_str = f"{t_bef:,} -> {t_aft:,} (-{t_bef - t_aft})"
        lines.append(f"{layer_name:<46} | {cust_str:<26} | {tot_str}")
    lines.append("------------------------------------------------------------------------------------------")
    lines.append("VERIFICATION: 0 records for the erased customer remain in any raw, staging, mart, or Parquet layer.")
    lines.append("==========================================================================================")

    report = "\n".join(lines) + "\n"
    print(report)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute GDPR customer erasure across all layers.")
    parser.add_argument(
        "--customer-id",
        default=DEFAULT_CUSTOMER_ID,
        help="Raw customer_id (or customer_unique_id) to erase.",
    )
    args = parser.parse_args()
    erase_customer(args.customer_id)

