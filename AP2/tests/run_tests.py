#!/usr/bin/env python3
"""Run independent SQL checks outside dbt against AP2/northmart.duckdb."""

from pathlib import Path
import sys
import duckdb


def run_tests() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    db_path = base_dir / "northmart.duckdb"
    if not db_path.exists():
        print(f"Error: Database {db_path} not found. Run src/init_db.py and the pipeline first.")
        sys.exit(1)

    con = duckdb.connect(str(db_path), read_only=True)
    test_sql_path = base_dir / "tests" / "test_referential_integrity.sql"
    queries = [q.strip() for q in test_sql_path.read_text(encoding="utf-8").split(";") if q.strip()]

    print("Running AP2 independent data quality checks:")
    all_passed = True
    try:
        for q in queries:
            rows = con.execute(q).fetchall()
            for test_name, fail_cnt, status in rows:
                print(f"[{status}] {test_name}: {fail_cnt} failures")
                if status != "PASS":
                    all_passed = False

        fact_cnt = con.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
        raw_cnt = con.execute("SELECT COUNT(*) FROM raw_api_orders").fetchone()[0]
        print(f"Row counts: raw_api_orders = {raw_cnt}, fact_sales = {fact_cnt}")
    finally:
        con.close()

    if all_passed:
        print("All checks passed.")
        sys.exit(0)
    else:
        print("Some checks failed.")
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
