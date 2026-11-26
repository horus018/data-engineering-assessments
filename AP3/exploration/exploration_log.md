# PA3 Part B — Task 4: Apache Spark (PySpark) Exploration Log

This log documents what we tried, what failed, and how we solved each problem while setting up and benchmarking **Apache Spark (`PySpark 4.3.0`, local mode)** on the NorthMart dataset.

---

## Attempt 1 — Starting a Local `SparkSession` on Linux (`JAVA_HOME` & Driver Bind Address)

- **What we tried:**
  Installed `pyspark==4.3.0` in our virtual environment (`.venv`) and ran a minimal script with `SparkSession.builder.appName("NorthMart").getOrCreate()`.
- **What failed / went wrong:**
  1. Spark printed verbose `WARN Utils: Your hostname resolves to a loopback address: 127.0.1.1` warnings and attempted to spin up the Spark Web UI on port `4040` (which collides when running two scripts back-to-back).
  2. Dozens of `INFO` and `WARN` JVM log lines cluttered the terminal output, hiding our query results.
- **How we solved it:**
  We explicitly configured the builder with:
  ```python
  spark = (
      SparkSession.builder.appName("NorthMart-PA3")
      .master("local[*]")
      .config("spark.driver.host", "127.0.0.1")
      .config("spark.ui.enabled", "false")
      .getOrCreate()
  )
  spark.sparkContext.setLogLevel("ERROR")
  ```
  Pinning `spark.driver.host = "127.0.0.1"`, disabling the Web UI during automated runs, and setting the log level to `"ERROR"` produced clean, deterministic output.

---

## Attempt 2 — Benchmarking Aggregations (The Lazy Evaluation Trap)

- **What we tried:**
  In our first benchmark draft, we timed `df = spark.sql(query)` without calling `.collect()` or `.show()`.
- **What failed / went wrong:**
  Spark reported an unrealistically fast query time of `~1.5 ms` — even faster than reading the file from disk! When we inspected why, we realized that `spark.sql(query)` and `.groupBy().agg()` are **lazy transformations**: Spark only builds the logical execution plan (DAG) and does not scan a single row of Parquet until an **action** is triggered.
- **How we solved it:**
  We called `spark.sql(query).collect()` inside the timed section (matching `con.execute(query).fetchall()` in DuckDB), forcing both engines to execute the full physical plan and materialize the exact same result rows in Python memory.

---

## Attempt 3 — Why Was PySpark Slow on `GROUP BY` and `JOIN`? (`spark.sql.shuffle.partitions = 200`)

- **What we tried:**
  When we ran Query 1 (`GROUP BY year_month`) and Query 3 (`INNER JOIN dim_product GROUP BY category_name`) with `.collect()`, PySpark took several hundred milliseconds on just `112,650` rows (`3.4 MB` Parquet), compared to `< 10 ms` in DuckDB.
- **What failed / went wrong:**
  By default, Spark sets `spark.sql.shuffle.partitions = 200` (designed for large multi-node clusters processing hundreds of gigabytes). For a `3.4 MB` file, splitting a `GROUP BY` shuffle across **200 separate tasks** means each task processes only `~560` rows while paying massive thread-scheduling and task-serialization overhead.
- **How we solved it:**
  We tuned `spark.sql.shuffle.partitions` down from `200` to `4` (matching local CPU cores), and tested both configurations (`p=200` vs `p=4`) in `exploration/spark_vs_duckdb_experiment.py`. Reducing shuffle partitions from `200` to `4` cut PySpark's warm execution time substantially, providing a clear architectural finding for Task 5 and Task 6.

