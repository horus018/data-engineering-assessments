#!/usr/bin/env python3
"""Initialize the AP3 DuckDB database with raw tables, protected dimensions, and optional 14-day backfill."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import duckdb


AP3_ROOT = Path(__file__).resolve().parent.parent


def load_dotenv_if_present() -> None:
    """Load NORTHMART_HASH_KEY from AP3/.env if not already in environment."""
    env_file = AP3_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _resolve_dbt_bin() -> str:
    venv_dbt = Path(sys.executable).parent / "dbt"
    if venv_dbt.exists():
        return str(venv_dbt)
    return shutil.which("dbt") or "dbt"


def init_ap3_database(db_path: Path, rebuild: bool = False, backfill: bool = False) -> None:
    """Create or reset AP3 tables in DuckDB and optionally backfill the 14-day May 2018 batch."""
    load_dotenv_if_present()
    if rebuild and db_path.exists():
        db_path.unlink()

    # Restore pristine raw JSON files from AP2/data/raw if available when rebuilding
    ap2_raw = AP3_ROOT.parent / "AP2" / "data" / "raw"
    ap3_raw = AP3_ROOT / "data" / "raw"
    if rebuild and ap2_raw.exists():
        ap3_raw.mkdir(parents=True, exist_ok=True)
        for day_dir in sorted(ap2_raw.glob("2018-05-*")):
            dest = ap3_raw / day_dir.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(day_dir, dest)

    build_sql = (AP3_ROOT / "sql" / "build_model.sql").read_text(encoding="utf-8")
    init_sql = (AP3_ROOT / "sql" / "init_ap2_db.sql").read_text(encoding="utf-8")

    prev_cwd = os.getcwd()
    os.chdir(AP3_ROOT)
    con = duckdb.connect(str(db_path))
    try:
        if rebuild or not _table_exists(con, "dim_date"):
            con.execute(build_sql)
        con.execute(init_sql)
    finally:
        con.close()
        os.chdir(prev_cwd)

    if backfill:
        from load_raw import load_raw_for_date

        dbt_bin = _resolve_dbt_bin()
        dbt_dir = AP3_ROOT / "dbt"
        env = os.environ.copy()
        env["NORTHMART_DUCKDB_PATH"] = str(db_path)

        # Build protected customer dimension and review staging once
        subprocess.run(
            [
                dbt_bin,
                "run",
                "--profiles-dir",
                str(dbt_dir),
                "--select",
                "stg_customers",
                "dim_customer",
                "stg_reviews",
            ],
            cwd=str(dbt_dir),
            env=env,
            check=True,
        )

        # Load all 14 days into raw_api_orders and run dbt staging -> quality gate -> fact_sales
        for day_num in range(1, 15):
            bdate = f"2018-05-{day_num:02d}"
            load_raw_for_date(bdate, db_path=db_path, raw_dir=ap3_raw)
            if bdate == "2018-05-09":
                continue  # Corrupted day blocked by dbt_test_staging gate
            subprocess.run(
                [
                    dbt_bin,
                    "run",
                    "--profiles-dir",
                    str(dbt_dir),
                    "--select",
                    "stg_orders",
                    "fact_sales",
                    "--vars",
                    f'{{"batch_date": "{bdate}"}}',
                ],
                cwd=str(dbt_dir),
                env=env,
                check=True,
            )

        # Keep stg_orders populated with 2018-05-01 so demo customer is visible in stg_orders too
        subprocess.run(
            [
                dbt_bin,
                "run",
                "--profiles-dir",
                str(dbt_dir),
                "--select",
                "stg_orders",
                "--vars",
                '{"batch_date": "2018-05-01"}',
            ],
            cwd=str(dbt_dir),
            env=env,
            check=True,
        )

        # Export curated Parquet files
        con = duckdb.connect(str(db_path))
        try:
            curated_dir = AP3_ROOT / "data" / "curated"
            curated_dir.mkdir(parents=True, exist_ok=True)
            part_dir = curated_dir / "fact_sales_partitioned"
            if part_dir.exists():
                shutil.rmtree(part_dir)
            con.execute(
                f"COPY fact_sales TO '{curated_dir / 'fact_sales.parquet'}' (FORMAT PARQUET, COMPRESSION ZSTD, OVERWRITE TRUE);"
            )
            con.execute(
                f"COPY fact_sales TO '{part_dir}' (FORMAT PARQUET, PARTITION_BY (year_month), COMPRESSION ZSTD, OVERWRITE TRUE);"
            )
        finally:
            con.close()

    con = duckdb.connect(str(db_path), read_only=True)
    try:
        counts = {
            t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in (
                "raw_customers",
                "raw_orders",
                "raw_order_reviews",
                "dim_date",
                "dim_product",
                "dim_customer",
                "dim_seller",
                "fact_sales",
                "raw_api_orders",
            )
        }
        print("AP3 database ready:", counts)
    finally:
        con.close()


def _table_exists(con: duckdb.DuckDBPyConnection, table_name: str) -> bool:
    row = con.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?",
        [table_name],
    ).fetchone()
    return bool(row and row[0] > 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize AP3 DuckDB database.")
    parser.add_argument(
        "--db",
        type=Path,
        default=AP3_ROOT / "northmart.duckdb",
        help="Path to the AP3 DuckDB file.",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Delete existing DuckDB file and rebuild tables from build_model.sql.",
    )
    parser.add_argument(
        "--backfill",
        action="store_true",
        help="Load all 14 May 2018 batches and build dbt protected models.",
    )
    args = parser.parse_args()
    init_ap3_database(args.db, rebuild=args.rebuild, backfill=args.backfill)
