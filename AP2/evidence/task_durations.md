# Airflow Task Durations Across 14-Day Backfill (2018-05-01 to 2018-05-14)

| Task ID | Runs | Succeeded | Failed | Upstream Failed | Avg Duration (s) | Min (s) | Max (s) | Total (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `dbt_run_staging` | 14 | 14 | 0 | 0 | **5.775** | 5.281 | 6.494 | 80.856 |
| `dbt_test_staging` | 14 | 13 | 1 | 0 | **4.675** | 4.084 | 5.251 | 65.451 |
| `dbt_run_marts` | 14 | 13 | 0 | 1 | **4.341** | 3.758 | 4.893 | 56.430 |
| `load_raw_orders` | 14 | 14 | 0 | 0 | **0.611** | 0.442 | 1.003 | 8.550 |
| `extract_orders` | 14 | 14 | 0 | 0 | **0.580** | 0.186 | 3.488 | 8.113 |
