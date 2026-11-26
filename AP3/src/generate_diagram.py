#!/usr/bin/env python3
"""Generate clean white-background architecture diagram for PA3 (architecture/gdpr_pipeline_ap3.png)."""

from pathlib import Path
import matplotlib.patches as patches
import matplotlib.pyplot as plt


AP3_ROOT = Path(__file__).resolve().parent.parent


def generate_ap3_diagram() -> None:
    fig, ax = plt.subplots(figsize=(14, 7.2), dpi=180, facecolor="#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7.2)
    ax.axis("off")

    ax.text(
        7.0,
        6.82,
        "PA3 Architecture: Part A (GDPR Data Protection) & Part B (Apache Spark Exploration)",
        fontsize=13.5,
        fontweight="bold",
        color="#1F2937",
        ha="center",
        va="center",
    )

    def draw_container(x, y, w, h, label):
        box = patches.FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.05,rounding_size=0.14",
            facecolor="#F3F4F6",
            edgecolor="#D1D5DB",
            linewidth=1.2,
        )
        ax.add_patch(box)
        ax.text(
            x + 0.25,
            y + h - 0.28,
            label,
            fontsize=10,
            fontweight="bold",
            color="#374151",
            ha="left",
            va="center",
        )

    def draw_card(x, y, w, h, title, lines, bg="#FFFFFF", border="#9CA3AF", title_color="#111827"):
        card = patches.FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.04,rounding_size=0.12",
            facecolor=bg,
            edgecolor=border,
            linewidth=1.5,
        )
        ax.add_patch(card)
        ax.text(
            x + w / 2,
            y + h - 0.34,
            title,
            fontsize=9.8,
            fontweight="bold",
            color=title_color,
            ha="center",
            va="center",
        )
        ax.text(
            x + w / 2,
            y + (h - 0.42) / 2,
            "\n".join(lines),
            fontsize=8.3,
            color="#4B5563",
            ha="center",
            va="center",
            linespacing=1.35,
        )

    def draw_arrow(x1, y1, x2, y2, color="#4B5563"):
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->,head_width=0.22,head_length=0.3", lw=1.5, color=color),
        )

    # =========================================================================
    # Top Container: Part A: Data Protection (GDPR Tasks 1, 2, 3)
    # =========================================================================
    draw_container(
        0.35,
        3.65,
        13.3,
        2.75,
        "Part A: GDPR Data Protection & Right to Erasure (NORTHMART_HASH_KEY stored outside Git in .env)",
    )

    y_a = 3.92
    h_a = 1.92
    w_a = 2.28

    draw_card(
        0.60,
        y_a,
        w_a,
        h_a,
        "1. Raw Layer",
        [
            "data/raw/*/*.json",
            "raw_api_orders (4,471)",
            "raw_customers (99,441)",
            "raw_order_reviews",
        ],
    )
    draw_arrow(2.92, y_a + h_a / 2, 3.22, y_a + h_a / 2)

    draw_card(
        3.25,
        y_a,
        w_a,
        h_a,
        "2. Inventory (Task 1)",
        [
            "Classify all fields:",
            "• identifier",
            "• quasi-identifier",
            "• non-personal",
            "Purpose + retention",
        ],
    )
    draw_arrow(5.57, y_a + h_a / 2, 5.87, y_a + h_a / 2)

    draw_card(
        5.90,
        y_a,
        w_a,
        h_a,
        "3. dbt Protect (Task 2)",
        [
            "sha256(KEY || customer_id)",
            "zip: 75650 -> 75XXX",
            "city: REDACTED",
            "Drops review comments",
        ],
        bg="#EFF6FF",
        border="#2563EB",
        title_color="#1D4ED8",
    )
    draw_arrow(8.22, y_a + h_a / 2, 8.52, y_a + h_a / 2, color="#16A34A")

    draw_card(
        8.55,
        y_a,
        w_a,
        h_a,
        "4. Safe Marts",
        [
            "dim_customer (hashed)",
            "fact_sales (4,059 rows,",
            "surrogate key only)",
            "data/curated/*.parquet",
        ],
        bg="#ECFDF5",
        border="#059669",
        title_color="#065F46",
    )
    draw_arrow(10.87, y_a + h_a / 2, 11.17, y_a + h_a / 2, color="#DC2626")

    draw_card(
        11.20,
        y_a,
        w_a,
        h_a,
        "5. Erasure (Task 3)",
        [
            "erase_customer.py + .sql",
            "Scrubs JSON, raw tables,",
            "staging, marts & Parquet",
            "Customer: 3 -> 0 rows",
        ],
        bg="#FEF2F2",
        border="#DC2626",
        title_color="#991B1B",
    )

    # =========================================================================
    # Bottom Container: Part B: Tool Exploration (Apache Spark Tasks 4, 5, 6)
    # =========================================================================
    draw_container(
        0.35,
        0.45,
        13.3,
        2.75,
        "Part B: Tool Exploration (Apache Spark PySpark 4.3.0, local[*] vs. DuckDB 2.0)",
    )

    y_b = 0.72
    h_b = 1.92
    w_b = 2.95

    draw_card(
        0.60,
        y_b,
        w_b,
        h_b,
        "1. Tool Setup",
        [
            "Apache Spark (PySpark 4.3.0)",
            "Local mode: local[*]",
            "Tuned shuffle.partitions = 4",
            "Input: 112,650 items (3.43 MB)",
        ],
    )
    draw_arrow(3.59, y_b + h_b / 2, 3.91, y_b + h_b / 2)

    draw_card(
        3.95,
        y_b,
        w_b,
        h_b,
        "2. Working Example (Task 4)",
        [
            "spark_working_example.py",
            "3-table join + state GMV",
            "Exploration log: solved JVM",
            "warnings & lazy .collect()",
        ],
    )
    draw_arrow(6.94, y_b + h_b / 2, 7.26, y_b + h_b / 2)

    draw_card(
        7.30,
        y_b,
        w_b,
        h_b,
        "3. Experiment (Task 5)",
        [
            "spark_vs_duckdb_experiment.py",
            "Q1 Warm: 5.5 ms vs 205.7 ms",
            "Q2 Warm: 4.7 ms vs 140.8 ms",
            "Q3 Warm: 13.5 ms vs 267.8 ms",
        ],
        bg="#EFF6FF",
        border="#2563EB",
        title_color="#1D4ED8",
    )
    draw_arrow(10.29, y_b + h_b / 2, 10.61, y_b + h_b / 2, color="#059669")

    draw_card(
        10.65,
        y_b,
        2.83,
        h_b,
        "4. Evaluation (Task 6)",
        [
            "DuckDB is 20x–38x faster",
            "No JVM or shuffle overhead",
            "Decision: keep DuckDB now;",
            "use Spark only > 100 GB",
        ],
        bg="#ECFDF5",
        border="#059669",
        title_color="#065F46",
    )

    out_path = AP3_ROOT / "architecture" / "gdpr_pipeline_ap3.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", facecolor="#FFFFFF")
    plt.close(fig)
    print("Saved clean diagram to", out_path)


if __name__ == "__main__":
    generate_ap3_diagram()
