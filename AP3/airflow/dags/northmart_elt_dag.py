"""
NorthMart AP3 Orchestrated & Privacy-Protected ELT Pipeline DAG.

Runs daily from 2018-05-01 to 2018-05-14 (catchup=True):
  1. extract_orders   - Fetch paginated orders from Mock REST API (retries HTTP 503)
  2. load_raw_orders  - Idempotently replace batch_date rows in DuckDB raw_api_orders
  3. dbt_run_staging  - Build stg_customers, dim_customer, stg_reviews, and stg_orders (with keyed SHA-256 hash)
  4. dbt_test_staging - Run dbt quality & privacy gate tests (stops bad batches!)
  5. dbt_run_marts    - Incrementally merge clean, pseudonymized batch into fact_sales
"""

from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import sys

from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG


AP3_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = AP3_ROOT / "src"
DBT_DIR = AP3_ROOT / "dbt"
DB_PATH = AP3_ROOT / "northmart.duckdb"
RAW_DIR = AP3_ROOT / "data" / "raw"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from extract_orders import extract_orders_for_date  # noqa: E402
from load_raw import load_raw_for_date  # noqa: E402


def _resolve_dbt_bin() -> str:
    venv_dbt = Path(sys.executable).parent / "dbt"
    if venv_dbt.exists():
        return str(venv_dbt)
    return shutil.which("dbt") or "dbt"


DBT_BIN = _resolve_dbt_bin()
ENV_LOAD = f"set -a && [ -f '{AP3_ROOT}/.env' ] && . '{AP3_ROOT}/.env' && set +a && "

default_args = {
    "owner": "northmart-data-eng",
    "depends_on_past": False,
    "retries": 0,
}

with DAG(
    dag_id="northmart_ap3_elt_pipeline",
    description="Daily GDPR-protected ELT pipeline: REST API -> DuckDB raw -> dbt pseudonymized staging + quality gate -> fact_sales",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2018, 5, 1, tzinfo=timezone.utc),
    end_date=datetime(2018, 5, 14, tzinfo=timezone.utc),
    catchup=True,
    max_active_runs=1,
    max_active_tasks=1,
    tags=["northmart", "ap3", "gdpr", "elt", "dbt", "duckdb"],
) as dag:

    extract_orders = PythonOperator(
        task_id="extract_orders",
        python_callable=extract_orders_for_date,
        op_kwargs={
            "batch_date": "{{ ds }}",
            "raw_dir": RAW_DIR,
        },
    )

    load_raw_orders = PythonOperator(
        task_id="load_raw_orders",
        python_callable=load_raw_for_date,
        op_kwargs={
            "batch_date": "{{ ds }}",
            "db_path": DB_PATH,
            "raw_dir": RAW_DIR,
        },
    )

    dbt_run_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command=(
            f"{ENV_LOAD}cd '{DBT_DIR}' && "
            f"NORTHMART_DUCKDB_PATH='{DB_PATH}' "
            f"'{DBT_BIN}' run --profiles-dir '{DBT_DIR}' "
            "--select stg_customers dim_customer stg_reviews stg_orders "
            "--vars '{\"batch_date\": \"{{ ds }}\"}'"
        ),
    )

    dbt_test_staging = BashOperator(
        task_id="dbt_test_staging",
        bash_command=(
            f"{ENV_LOAD}cd '{DBT_DIR}' && "
            f"NORTHMART_DUCKDB_PATH='{DB_PATH}' "
            f"'{DBT_BIN}' test --profiles-dir '{DBT_DIR}' "
            "--vars '{\"batch_date\": \"{{ ds }}\"}'"
        ),
    )

    dbt_run_marts = BashOperator(
        task_id="dbt_run_marts",
        bash_command=(
            f"{ENV_LOAD}cd '{DBT_DIR}' && "
            f"NORTHMART_DUCKDB_PATH='{DB_PATH}' "
            f"'{DBT_BIN}' run --profiles-dir '{DBT_DIR}' "
            "--select fact_sales --vars '{\"batch_date\": \"{{ ds }}\"}'"
        ),
    )

    extract_orders >> load_raw_orders >> dbt_run_staging >> dbt_test_staging >> dbt_run_marts

