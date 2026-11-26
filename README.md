# NorthMart Data Platform — Data Engineering (2026/2027)

**Group 4 Members:**
- **Lucas Alves Rubira** (`a67707`)
- **Dorota Dudkowiak** (`m324637`)
- **Aye Khine Lwin** (`a70733`)

---

## Repository Structure

This repository contains all three Practical Assessments for the NorthMart Data Platform:
- **[AP1/](AP1/README.md) — Practical Assessment 1:** Raw Data Profiling, Kimball Star Schema in DuckDB, and CSV vs. Parquet Storage Benchmarks.
- **[AP2/](AP2/README.md) — Practical Assessment 2:** Orchestrated and Tested Daily ELT Pipeline (FastAPI Mock REST API, Idempotent DuckDB Raw Loader, `dbt` Staging & Incremental Fact Table, 20 Quality Gate Tests, and Apache Airflow DAG).
- **[AP3/](AP3/README.md) — Practical Assessment 3:** GDPR Data Protection (Personal Data Inventory, Keyed SHA-256 Hashing & Location Generalization in `dbt`, GDPR Art. 17 Multi-Layer Customer Erasure) and Emerging Tool Exploration (Apache Spark / PySpark vs. DuckDB Benchmark).

---

## Quick Reproduction Guide for PA3 (`AP3/`)

```bash
cd AP3
source ../.venv/bin/activate
export NORTHMART_HASH_KEY="northmart_gdpr_secret_key_2026"

# 1. Initialize database, build protected dbt models, and backfill May 2018
python src/init_db.py --rebuild --backfill

# 2. Execute GDPR Art. 17 customer erasure across all layers (raw JSON, raw tables, staging, marts, Parquet)
python src/erase_customer.py --customer-id d1806517abdeab70d77e1ff58ec5f1b8

# 3. Run automated 8-check referential integrity & GDPR verification suite
python tests/run_tests.py

# 4. Run Part B Apache Spark minimal working example and Spark vs. DuckDB experiment
python exploration/spark_working_example.py
python exploration/spark_vs_duckdb_experiment.py
```

For full written answers to **PA3 Tasks 1–6**, see **[AP3/README.md](AP3/README.md)**.
