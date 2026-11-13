# Data Engineering Practical Assessments (2026/2027)

**Institution**: Universidade Politecnica de Braganca (UPB)  
**Academic Year**: 2026/2027  
**Course**: Data Engineering  

### Group Members

| Name | Student Number |
| :--- | :--- |
| Lucas Alves Rubira | a67707 |
| Dorota Dudkowiak | m324637 |
| Aye Khine Lwin | a70733 |

## Repository Structure

- `AP1/`: Assessment 1 (Storage formats, data profiling, Kimball star schema in DuckDB, and Parquet benchmarks)
  - `AP1/README.md`: Documentation and written answers for AP1
  - `AP1/sql/`: `profiling.sql`, `build_model.sql`, `benchmark.sql`
  - `AP1/src/`: Benchmark runner and diagram scripts
  - `AP1/tests/`: SQL referential integrity checks
  - `AP1/evidence/`: Profiling and benchmark outputs
- `AP2/`: Assessment 2 (Orchestrated and tested ELT pipeline with FastAPI, DuckDB, dbt, and Airflow)
  - `AP2/README.md`: Documentation, architecture diagram, and answers to Tasks 1 to 6
  - `AP2/mock_api.py`: Mock NorthMart orders REST API (`:8000`)
  - `AP2/src/`: `init_db.py`, `extract_orders.py`, `load_raw.py`, `generate_diagram.py`
  - `AP2/dbt/`: Staging model (`stg_orders`), 20 quality tests, and incremental mart (`fact_sales`)
  - `AP2/airflow/dags/`: `northmart_elt_dag.py` (daily schedule, 14-day backfill, `max_active_runs=1`)
  - `AP2/tests/`: Independent SQL verification suite (`run_tests.py`)
  - `AP2/evidence/`: Airflow Grid View screenshot, dbt test logs, idempotency check, and task durations
- `AP3/`: Assessment 3 (Upcoming)
- `requirements.txt`: Pinned Python 3.12 dependencies for AP1 and AP2

## Assessment Summary

| Assessment | Topic | Status | Weight |
| :--- | :--- | :--- | :--- |
| AP1 | Storage Formats and Analytical Modelling (DuckDB, Parquet, Star Schema) | Completed | 20% |
| AP2 | Orchestrated and Tested ELT Pipeline (REST API, dbt, Airflow) | Completed | 20% |
| AP3 | Data Protection and Tool Exploration | Upcoming | 20% |

## Quick Start (AP2)

```bash
# 1. Create Python 3.12 virtual environment and install dependencies
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r AP2/requirements.txt

# 2. Initialize fresh AP2 DuckDB database (AP1 dimensions intact, fact_sales empty)
cd AP2
python src/init_db.py --rebuild

# 3. Start the Mock API (Terminal 1)
uvicorn mock_api:app --port 8000

# 4. Start Airflow (Terminal 2)
export AIRFLOW_HOME="$(pwd)/airflow"
export AIRFLOW__CORE__DAGS_FOLDER="$(pwd)/airflow/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
airflow db migrate && airflow standalone

# 5. Unpause the DAG to run the 14-day backfill (Terminal 3)
airflow dags unpause northmart_ap2_elt_pipeline

# 6. Run independent SQL verification checks
python tests/run_tests.py
```

See [AP1/README.md](AP1/README.md) and [AP2/README.md](AP2/README.md) for full details.
