#!/usr/bin/env python3
"""
PA3 Part B — Task 4: Minimal Working Example with Apache Spark (PySpark, local mode).

Loads NorthMart's order items, orders, and customers into PySpark DataFrames,
computes revenue and order counts by customer state, and saves the output to
evidence/spark_working_example_output.txt.
"""

from pathlib import Path
import time
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


AP3_ROOT = Path(__file__).resolve().parent.parent


def run_working_example() -> None:
    t0 = time.perf_counter()
    spark = (
        SparkSession.builder.appName("NorthMart-PA3-WorkingExample")
        .master("local[*]")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    startup_ms = (time.perf_counter() - t0) * 1000.0

    try:
        source_dir = AP3_ROOT / "data" / "source"
        orders_df = spark.read.csv(
            str(source_dir / "olist_orders_dataset.csv"),
            header=True,
            inferSchema=True,
        )
        items_df = spark.read.csv(
            str(source_dir / "olist_order_items_dataset.csv"),
            header=True,
            inferSchema=True,
        )
        customers_df = spark.read.csv(
            str(source_dir / "olist_customers_dataset.csv"),
            header=True,
            inferSchema=True,
        )

        # Join orders -> order_items -> customers and aggregate top 10 states by gross revenue
        t_query = time.perf_counter()
        state_summary_df = (
            items_df.join(orders_df, on="order_id", how="inner")
            .join(customers_df, on="customer_id", how="inner")
            .withColumn("total_item_value", F.col("price") + F.col("freight_value"))
            .groupBy("customer_state")
            .agg(
                F.count("*").alias("items_sold"),
                F.countDistinct("order_id").alias("distinct_orders"),
                F.round(F.sum("price"), 2).alias("merchandise_revenue"),
                F.round(F.sum("total_item_value"), 2).alias("total_gmv"),
            )
            .orderBy(F.col("total_gmv").desc())
            .limit(10)
        )
        rows = state_summary_df.collect()
        query_ms = (time.perf_counter() - t_query) * 1000.0

        lines = [
            "==========================================================================================",
            "NORTHMART PA3 — TASK 4: APACHE SPARK (PYSPARK LOCAL MODE) MINIMAL WORKING EXAMPLE",
            "==========================================================================================",
            f"Spark Version                      : {spark.version}",
            f"Master / Execution Mode            : local[*] (spark.sql.shuffle.partitions=4)",
            f"SparkSession JVM Startup Time      : {startup_ms:.2f} ms",
            f"3-Table Join + Aggregation Time    : {query_ms:.2f} ms",
            "------------------------------------------------------------------------------------------",
            f"{'State':<8} | {'Items Sold':>12} | {'Distinct Orders':>16} | {'Merchandise Rev ($)':>20} | {'Total GMV ($)':>16}",
            "------------------------------------------------------------------------------------------",
        ]
        for r in rows:
            lines.append(
                f"{r['customer_state']:<8} | {r['items_sold']:>12,} | {r['distinct_orders']:>16,} | "
                f"{r['merchandise_revenue']:>20,.2f} | {r['total_gmv']:>16,.2f}"
            )
        lines.append("==========================================================================================")

        output = "\n".join(lines) + "\n"
        print(output)
        out_path = AP3_ROOT / "evidence" / "spark_working_example_output.txt"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
    finally:
        spark.stop()


if __name__ == "__main__":
    run_working_example()

