"""
NorthMart AP2 Orchestrated ELT Pipeline DAG.

Runs daily from 2018-05-01 to 2018-05-14 (catchup=True):
  1. extract_orders   - Fetch paginated orders from Mock REST API (retries HTTP 503)
  2. load_raw_orders  - Idempotently replace batch_date rows in DuckDB raw_api_orders
  3. dbt_run_staging  - Build stg_orders (typed & cleaned staging table)
  4. dbt_test_staging - Run 20 dbt quality gate tests (stops bad batches!)
  5. dbt_run_marts    - Incrementally merge clean batch into fact_sales
"""

from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys

from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG


AP2_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = AP2_ROOT / "src"
DBT_DIR = AP2_ROOT / "dbt"
DB_PATH = AP2_ROOT / "northmart.duckdb"
RAW_DIR = AP2_ROOT / "data" / "raw"

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

default_args = {
    "owner": "northmart-data-eng",
    "depends_on_past": False,
    "retries": 0,
}

with DAG(
    dag_id="northmart_ap2_elt_pipeline",
    description="Daily ELT pipeline: REST API -> DuckDB raw -> dbt staging + quality gate -> fact_sales",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2018, 5, 1, tzinfo=timezone.utc),
    end_date=datetime(2018, 5, 14, tzinfo=timezone.utc),
    catchup=True,
    max_active_runs=1,   # DuckDB allows one writer at a time during backfill
    max_active_tasks=1,
    tags=["northmart", "ap2", "elt", "dbt", "duckdb"],
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
            f"cd '{DBT_DIR}' && "
            f"NORTHMART_DUCKDB_PATH='{DB_PATH}' "
            f"'{DBT_BIN}' run --profiles-dir '{DBT_DIR}' "
            "--select stg_orders --vars '{\"batch_date\": \"{{ ds }}\"}'"
        ),
    )

    dbt_test_staging = BashOperator(
        task_id="dbt_test_staging",
        bash_command=(
            f"cd '{DBT_DIR}' && "
            f"NORTHMART_DUCKDB_PATH='{DB_PATH}' "
            f"'{DBT_BIN}' test --profiles-dir '{DBT_DIR}' "
            "--vars '{\"batch_date\": \"{{ ds }}\"}'"
        ),
    )

    dbt_run_marts = BashOperator(
        task_id="dbt_run_marts",
        bash_command=(
            f"cd '{DBT_DIR}' && "
            f"NORTHMART_DUCKDB_PATH='{DB_PATH}' "
            f"'{DBT_BIN}' run --profiles-dir '{DBT_DIR}' "
            "--select fact_sales --vars '{\"batch_date\": \"{{ ds }}\"}'"
        ),
    )

    extract_orders >> load_raw_orders >> dbt_run_staging >> dbt_test_staging >> dbt_run_marts

