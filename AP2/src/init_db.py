#!/usr/bin/env python3
"""Initialize the fresh AP2 DuckDB database from AP1's star schema dimensions."""

import argparse
import os
from pathlib import Path
import duckdb


AP2_ROOT = Path(__file__).resolve().parent.parent


def init_ap2_database(db_path: Path, rebuild_from_ap1: bool = False) -> None:
    """Create or reset AP2 tables in DuckDB."""
    if rebuild_from_ap1 and db_path.exists():
        db_path.unlink()

    build_sql = (AP2_ROOT / "sql" / "build_model.sql").read_text(encoding="utf-8")
    init_sql = (AP2_ROOT / "sql" / "init_ap2_db.sql").read_text(encoding="utf-8")

    prev_cwd = os.getcwd()
    os.chdir(AP2_ROOT)
    con = duckdb.connect(str(db_path))
    try:
        if rebuild_from_ap1 or not _table_exists(con, "dim_date"):
            con.execute(build_sql)
        con.execute(init_sql)

        counts = {
            t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in ("dim_date", "dim_product", "dim_customer", "dim_seller", "fact_sales", "raw_api_orders")
        }
        print("AP2 database initialized:", counts)
    finally:
        con.close()
        os.chdir(prev_cwd)


def _table_exists(con: duckdb.DuckDBPyConnection, table_name: str) -> bool:
    row = con.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?",
        [table_name],
    ).fetchone()
    return bool(row and row[0] > 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize AP2 DuckDB database.")
    parser.add_argument(
        "--db",
        type=Path,
        default=AP2_ROOT / "northmart.duckdb",
        help="Path to the AP2 DuckDB file.",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Delete existing DuckDB file and rebuild dimensions from AP1 build_model.sql.",
    )
    args = parser.parse_args()
    init_ap2_database(args.db, rebuild_from_ap1=args.rebuild)
