#!/usr/bin/env python3
"""Run automated PA3 verification suite (referential integrity + GDPR protection & erasure)."""

from pathlib import Path
import sys
import duckdb


AP3_ROOT = Path(__file__).resolve().parent.parent


def run_verification_suite(db_path: Path = AP3_ROOT / "northmart.duckdb") -> None:
    sql_path = AP3_ROOT / "tests" / "test_referential_integrity.sql"
    sql = sql_path.read_text(encoding="utf-8")

    con = duckdb.connect(str(db_path), read_only=True)
    try:
        rows = con.execute(sql).fetchall()
    finally:
        con.close()

    lines = [
        "================================================================================",
        "NORTHMART PA3 — AUTOMATED INTEGRITY & GDPR PRIVACY VERIFICATION SUITE",
        "================================================================================",
        f"{'Check Name':<54} | {'Violations':>10} | {'Status':<8}",
        "--------------------------------------------------------------------------------",
    ]
    failed = 0
    for check_name, violations, status in rows:
        lines.append(f"{check_name:<54} | {violations:>10} | {status:<8}")
        if status != "PASSED":
            failed += 1
    lines.append("================================================================================")

    report = "\n".join(lines) + "\n"
    print(report)
    out_file = AP3_ROOT / "evidence" / "referential_checks_output.txt"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(report, encoding="utf-8")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_verification_suite()
