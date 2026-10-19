#!/usr/bin/env python3
"""
Automated Data Quality & Referential Integrity Test Runner for AP1.
"""

import duckdb
import sys
import os

def run_tests():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(base_dir, "northmart.duckdb")
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found. Run build_model.sql first.")
        sys.exit(1)

    con = duckdb.connect(db_path)
    test_sql_path = os.path.join(base_dir, "tests", "test_referential_integrity.sql")
    with open(test_sql_path, "r") as f:
        queries = [q.strip() for q in f.read().split(";") if q.strip()]

    print("==================================================")
    print("      NORTHMART AP1 DATA QUALITY TEST SUITE       ")
    print("==================================================")
    all_passed = True
    for q in queries:
        rows = con.execute(q).fetchall()
        for test_name, fail_cnt, status in rows:
            print(f"[{status}] {test_name}: {fail_cnt} failures")
            if status != "PASS":
                all_passed = False

    print("==================================================")
    if all_passed:
        print("ALL TESTS PASSED! Dimensional model is verified.")
        sys.exit(0)
    else:
        print("TEST FAILURES DETECTED!")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
