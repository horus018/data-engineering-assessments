#!/usr/bin/env python3
"""
Generate the NorthMart AP2 ELT Pipeline Architecture diagram (architecture/pipeline_ap2.png).
Uses matplotlib to render a clean visual overview of the 5-task Airflow + dbt pipeline.
"""

from pathlib import Path
import matplotlib.patches as patches
import matplotlib.pyplot as plt


def create_pipeline_diagram(output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(16, 8.5), facecolor="#0D0E23")
    ax.set_facecolor("#0D0E23")
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8.5)
    ax.axis("off")

    c_card = "#191A2F"
    c_teal = "#81F3E5"
    c_accent = "#006A62"
    c_white = "#FBF8FF"
    c_muted = "#B6B8D6"
    c_red = "#FFB4AB"
    c_red_bg = "#3A1B24"
    c_blue = "#1E3A5F"

    # Title
    ax.text(
        8.0,
        7.95,
        "NorthMart AP2 — Orchestrated & Tested ELT Pipeline",
        fontsize=20,
        fontweight="bold",
        color=c_white,
        ha="center",
        va="center",
    )
    ax.text(
        8.0,
        7.45,
        "Airflow DAG (northmart_ap2_elt_pipeline) · Daily Schedule · 14-Day Backfill (2018-05-01 to 2018-05-14) · Idempotent",
        fontsize=11,
        color=c_teal,
        ha="center",
        va="center",
    )

    # Outer Airflow DAG container
    dag_box = patches.FancyBboxPatch(
        (2.8, 2.5),
        12.7,
        4.3,
        boxstyle="round,pad=0.06,rounding_size=0.18",
        facecolor="#121329",
        edgecolor="#2D325A",
        linewidth=1.5,
        linestyle="--",
    )
    ax.add_patch(dag_box)
    ax.text(
        9.15,
        6.55,
        "Airflow DAG (max_active_runs = 1, single DuckDB writer)",
        fontsize=10.5,
        fontweight="bold",
        color=c_muted,
        ha="center",
        va="center",
    )

    def draw_box(x, y, w, h, title, subtitle, header_color=c_blue, border_color=c_teal, title_color=c_white):
        card = patches.FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.04,rounding_size=0.14",
            facecolor=c_card,
            edgecolor=border_color,
            linewidth=1.6,
        )
        ax.add_patch(card)
        header = patches.FancyBboxPatch(
            (x, y + h - 0.5),
            w,
            0.5,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor=header_color,
            edgecolor="none",
        )
        ax.add_patch(header)
        ax.text(x + w / 2, y + h - 0.25, title, fontsize=10, fontweight="bold", color=title_color, ha="center", va="center")
        ax.text(x + w / 2, y + (h - 0.5) / 2, subtitle, fontsize=8.8, color=c_muted, ha="center", va="center", linespacing=1.4)

    def draw_arrow(x1, y1, x2, y2, color=c_teal, label=None, lx=None, ly=None):
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(arrowstyle="-|>,head_width=0.25,head_length=0.4", color=color, lw=1.8),
        )
        if label:
            ax.text(lx or (x1 + x2) / 2, ly or (y1 + y2) / 2 + 0.18, label, fontsize=8.5, fontweight="bold", color=color, ha="center", va="center")

    # External Mock API
    draw_box(
        0.35,
        4.35,
        2.05,
        1.7,
        "Mock REST API",
        "FastAPI :8000\nGET /orders\n100 items / page\n~10% HTTP 503",
        header_color="#2A2D4F",
        border_color="#5B6199",
    )

    # 5 Airflow Tasks
    draw_box(3.05, 4.35, 2.15, 1.7, "1. extract_orders", "PythonOperator\nPagination +\nExponential Retry\n-> data/raw/", header_color=c_blue)
    draw_box(5.55, 4.35, 2.15, 1.7, "2. load_raw_orders", "PythonOperator\nAtomic Transaction\nDELETE + INSERT\n-> raw_api_orders", header_color=c_blue)
    draw_box(8.05, 4.35, 2.15, 1.7, "3. dbt_run_staging", "BashOperator\ndbt run stg_orders\nType, Cast, Clean\nNo Silent Drops", header_color=c_blue)
    draw_box(10.55, 4.35, 2.25, 1.7, "4. dbt_test_staging", "Quality Gate (20 tests)\nUnique, Not-Null,\nFKs, Ranges,\nOrder Economics", header_color=c_accent, border_color=c_teal)
    draw_box(13.15, 4.35, 2.15, 1.7, "5. dbt_run_marts", "BashOperator\ndbt incremental\ndelete+insert\n-> fact_sales", header_color=c_accent, border_color=c_teal)

    # Failure Gate Box
    draw_box(
        10.55,
        2.7,
        2.25,
        1.15,
        "GATE FAILS (2018-05-09)",
        "4 tests fail · DAG stops\nfact_sales untouched (0 bad rows)",
        header_color=c_red_bg,
        border_color=c_red,
        title_color=c_red,
    )

    # Storage Layer Bottom Strip
    draw_box(3.05, 0.55, 2.6, 1.45, "Raw JSON Layer", "data/raw/YYYY-MM-DD/\npage_*.json (unchanged)", header_color="#242645", border_color="#494E7A")
    draw_box(6.2, 0.55, 3.3, 1.45, "DuckDB Raw + Staging", "raw_api_orders (4,471 rows)\nstg_orders (batch_date scoped)", header_color="#242645", border_color="#494E7A")
    draw_box(10.05, 0.55, 5.25, 1.45, "DuckDB Star Schema Marts", "fact_sales (4,059 clean rows across 13 days)\n+ AP1 Conformed Dimensions (dim_date, dim_product, dim_customer, dim_seller)", header_color=c_accent, border_color=c_teal)

    # Arrows between tasks
    draw_arrow(2.42, 5.2, 3.03, 5.2)
    draw_arrow(5.22, 5.2, 5.53, 5.2)
    draw_arrow(7.72, 5.2, 8.03, 5.2)
    draw_arrow(10.22, 5.2, 10.53, 5.2)
    draw_arrow(12.82, 5.2, 13.13, 5.2)
    ax.text(12.97, 5.42, "PASS", fontsize=7.5, fontweight="bold", color=c_teal, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="#0D0E23", edgecolor="none"))
    draw_arrow(11.67, 4.33, 11.67, 3.88, color=c_red, label="FAIL", lx=12.02, ly=4.12)

    # Storage Arrows
    draw_arrow(4.12, 4.33, 4.12, 2.04, color="#6E74A8")
    draw_arrow(6.62, 4.33, 7.35, 2.04, color="#6E74A8")
    draw_arrow(9.12, 4.33, 8.45, 2.04, color="#6E74A8")
    draw_arrow(14.22, 4.33, 13.65, 2.04, color=c_teal)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(pad=0.3)
    plt.savefig(output_path, dpi=200, facecolor="#0D0E23")
    plt.close(fig)
    print(f"Generated {output_path}")


if __name__ == "__main__":
    ap2_root = Path(__file__).resolve().parent.parent
    create_pipeline_diagram(ap2_root / "architecture" / "pipeline_ap2.png")
