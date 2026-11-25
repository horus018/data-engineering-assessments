# Data Engineering Practical Assessments (2026/2027)

**Institution**: Universidade Politécnica de Bragança (UPB)  
**Academic Year**: 2026/2027  
**Course**: Data Engineering  

### Group Members

| Name | Student Number |
| :--- | :--- |
| Lucas Alves Rubira | a67707 |
| Dorota Dudkowiak | m324637 |
| Aye Khine Lwin | a70733 |

---

## Repository Overview

This repository hosts the practical coursework platform developed across three sequential assessments (**AP1**, **AP2**, and **AP3**) for the **Data Engineering** course:

```
project/
├── AP1/                        # Assessment 1: Storage formats & analytical modelling (COMPLETED)
│   ├── README.md               # Written answers, profiling, Kimball modelling, benchmarks & Lakehouse evaluation
│   ├── requirements.txt        # AP1 dependencies
│   ├── architecture/           # Star schema diagram (PNG and Mermaid)
│   ├── sql/                    # profiling.sql, build_model.sql, benchmark.sql
│   ├── src/                    # Benchmark and diagram scripts
│   ├── tests/                  # SQL referential integrity checks
│   └── evidence/               # Profiling, benchmark, and integrity logs
├── AP2/                        # Assessment 2: Orchestrated and tested ELT pipeline (COMPLETED)
│   ├── README.md               # AP2 guide, pipeline architecture, and answers to Tasks 1–6
│   ├── requirements.txt        # Pinned Airflow, DuckDB, dbt-duckdb, FastAPI, uvicorn, requests
│   ├── mock_api.py             # Mock NorthMart orders REST API (:8000)
│   ├── architecture/           # Pipeline diagrams (pipeline_ap2.png, pipeline_ap2.mmd)
│   ├── data/
│   │   ├── source/             # Olist CSVs, seller JSON, northmart_api_feed.parquet (gitignored)
│   │   ├── raw/                # Unchanged daily API JSON pages (gitignored)
│   │   └── curated/            # Parquet outputs
│   ├── sql/                    # build_model.sql and init_ap2_db.sql
│   ├── src/                    # init_db.py, extract_orders.py, load_raw.py, generate_diagram.py
│   ├── dbt/                    # Staging model, 20 dbt tests (incl. custom macro & business rule), incremental fact_sales
│   ├── airflow/dags/           # northmart_elt_dag.py (daily, 14-day backfill, max_active_runs=1)
│   ├── tests/                  # Independent SQL integrity checks outside dbt
│   └── evidence/               # Airflow Grid View PNG, dbt test logs, idempotency check, task durations
├── AP3/                        # Assessment 3: Data protection & tool exploration (Upcoming)
├── requirements.txt            # Pinned AP2/AP1 project requirements (Python 3.12)
└── .gitignore                  # Ignores raw data, DuckDB files, Airflow/dbt runtime state, study guides
```

---

## Practical Assessment Status

| Assessment | Scope | Status | Weight | Submission | Defense |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **AP1 (PA1)** | **Storage Formats & Analytical Modelling (Star Schema, DuckDB, Parquet)** | **COMPLETED** | **20%** | **17/10/2026** | **19/10/2026** |
| **AP2 (PA2)** | **Orchestrated & Tested ELT Pipeline (FastAPI mock, dbt, Airflow)** | **COMPLETED** | **20%** | **14/11/2026** | **16/11/2026** |
| **AP3 (PA3)** | Data Protection (GDPR erasure, hashing) & Tool Exploration | Upcoming | 20% | 12/12/2026 | 14/12/2026 |

---

## Quick Start (AP2)

To reproduce the AP2 orchestrated ELT pipeline:

```bash
# 1. Create Python 3.12 virtual environment and install pinned requirements
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r AP2/requirements.txt

# 2. Initialize fresh AP2 DuckDB (dimensions intact, fact_sales empty)
cd AP2
python src/init_db.py --rebuild

# 3. Start the Mock REST API (Terminal 1)
uvicorn mock_api:app --port 8000

# 4. Initialize and start Airflow (Terminal 2)
export AIRFLOW_HOME="$(pwd)/airflow"
export AIRFLOW__CORE__DAGS_FOLDER="$(pwd)/airflow/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
airflow db migrate && airflow standalone

# 5. Unpause DAG to execute the 14-day backfill (Terminal 3)
airflow dags unpause northmart_ap2_elt_pipeline

# 6. Run independent verification checks
python tests/run_tests.py
```

For full documentation, step-by-step explanations, and written answers for both assessments, see:
- [AP1/README.md](AP1/README.md)
- [AP2/README.md](AP2/README.md)
