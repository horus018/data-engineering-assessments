#!/usr/bin/env python3
"""Generate the AP2 diagrams (architecture/pipeline_ap2.png and architecture/star_schema.png)."""

from pathlib import Path
import matplotlib.patches as patches
import matplotlib.pyplot as plt


def create_pipeline_diagram(output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13, 5.2), facecolor="#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 5.2)
    ax.axis("off")

    ax.text(
        6.5,
        4.85,
        "AP2 Pipeline: Daily Airflow DAG with dbt Quality Gate",
        fontsize=13,
        fontweight="bold",
        color="#1F2937",
        ha="center",
        va="center",
    )

    dag_box = patches.FancyBboxPatch(
        (2.3, 0.45),
        10.4,
        3.95,
        boxstyle="round,pad=0.05,rounding_size=0.12",
        facecolor="#F3F4F6",
        edgecolor="#D1D5DB",
        linewidth=1.2,
    )
    ax.add_patch(dag_box)
    ax.text(
        7.5,
        4.15,
        "Airflow DAG (northmart_ap2_elt_pipeline, daily, 14-day backfill, max_active_runs=1)",
        fontsize=9.5,
        fontweight="bold",
        color="#374151",
        ha="center",
        va="center",
    )

    def draw_box(x, y, w, h, title, lines, bg="#FFFFFF", border="#9CA3AF", title_col="#111827"):
        box = patches.FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.03,rounding_size=0.08",
            facecolor=bg,
            edgecolor=border,
            linewidth=1.4,
        )
        ax.add_patch(box)
        ax.text(
            x + w / 2,
            y + h - 0.32,
            title,
            fontsize=9.5,
            fontweight="bold",
            color=title_col,
            ha="center",
            va="center",
        )
        ax.text(
            x + w / 2,
            y + (h - 0.35) / 2,
            "\n".join(lines),
            fontsize=8.2,
            color="#4B5563",
            ha="center",
            va="center",
            linespacing=1.35,
        )

    def draw_arrow(x1, y1, x2, y2, color="#4B5563", label=None, lx=None, ly=None):
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->", color=color, lw=1.4),
        )
        if label:
            ax.text(
                lx if lx is not None else (x1 + x2) / 2,
                ly if ly is not None else (y1 + y2) / 2 + 0.14,
                label,
                fontsize=8,
                color=color,
                ha="center",
                va="center",
            )

    draw_box(
        0.25,
        2.35,
        1.7,
        1.3,
        "Mock API",
        ["FastAPI :8000", "GET /orders", "JSON, 100/page"],
        bg="#FFFFFF",
        border="#9CA3AF",
    )

    draw_box(
        2.55,
        2.35,
        1.7,
        1.3,
        "1. Extract",
        ["extract_orders", "pagination + retry", "data/raw/*.json"],
    )
    draw_box(
        4.55,
        2.35,
        1.7,
        1.3,
        "2. Load Raw",
        ["load_raw_orders", "delete + insert", "raw_api_orders"],
    )
    draw_box(
        6.55,
        2.35,
        1.7,
        1.3,
        "3. dbt Staging",
        ["dbt_run_staging", "cast and clean", "stg_orders"],
    )
    draw_box(
        8.55,
        2.35,
        1.75,
        1.3,
        "4. dbt Tests",
        ["dbt_test_staging", "20 quality checks", "(gate)"],
        bg="#ECFDF5",
        border="#059669",
        title_col="#065F46",
    )
    draw_box(
        10.65,
        2.35,
        1.8,
        1.3,
        "5. dbt Marts",
        ["dbt_run_marts", "incremental load", "fact_sales"],
        bg="#ECFDF5",
        border="#059669",
        title_col="#065F46",
    )

    draw_box(
        8.55,
        0.7,
        1.75,
        1.1,
        "Run stops",
        ["2018-05-09 fails", "fact_sales untouched"],
        bg="#FEF2F2",
        border="#DC2626",
        title_col="#991B1B",
    )

    draw_arrow(1.97, 3.0, 2.53, 3.0)
    draw_arrow(4.27, 3.0, 4.53, 3.0)
    draw_arrow(6.27, 3.0, 6.53, 3.0)
    draw_arrow(8.27, 3.0, 8.53, 3.0)
    draw_arrow(10.32, 3.0, 10.63, 3.0, color="#059669", label="pass", lx=10.47, ly=3.18)
    draw_arrow(9.42, 2.33, 9.42, 1.82, color="#DC2626", label="fail", lx=9.65, ly=2.08)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(pad=0.25)
    plt.savefig(output_path, dpi=180, facecolor="#FFFFFF")
    plt.close(fig)
    print(f"Saved {output_path}")


def create_star_schema_diagram(output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7.5), facecolor="#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    ax.text(
        6.0,
        7.1,
        "NorthMart Star Schema (DuckDB)",
        fontsize=13,
        fontweight="bold",
        color="#1F2937",
        ha="center",
        va="center",
    )

    def draw_table(x, y, w, h, title, rows, header_bg="#E5E7EB"):
        box = patches.FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor="#FFFFFF",
            edgecolor="#9CA3AF",
            linewidth=1.3,
        )
        ax.add_patch(box)
        header = patches.FancyBboxPatch(
            (x, y + h - 0.42),
            w,
            0.42,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor=header_bg,
            edgecolor="#9CA3AF",
            linewidth=1.1,
        )
        ax.add_patch(header)
        ax.text(
            x + w / 2,
            y + h - 0.21,
            title,
            fontsize=9.5,
            fontweight="bold",
            color="#111827",
            ha="center",
            va="center",
        )
        step = (h - 0.55) / max(len(rows), 1)
        for idx, (col, dtype) in enumerate(rows):
            ry = y + h - 0.65 - idx * step
            ax.text(x + 0.14, ry, col, fontsize=8, color="#1F2937", ha="left", va="center")
            ax.text(x + w - 0.14, ry, dtype, fontsize=7.8, color="#6B7280", ha="right", va="center")

    draw_table(
        0.5,
        4.1,
        3.2,
        2.5,
        "dim_date",
        [
            ("PK date_key", "INTEGER"),
            ("date", "DATE"),
            ("year, month, quarter", "INTEGER"),
            ("day_of_week", "VARCHAR"),
            ("year_month", "VARCHAR"),
            ("is_weekend", "BOOLEAN"),
        ],
    )

    draw_table(
        8.3,
        4.1,
        3.2,
        2.5,
        "dim_product",
        [
            ("PK product_key", "INTEGER"),
            ("product_id", "VARCHAR"),
            ("category_name", "VARCHAR"),
            ("category_name_pt", "VARCHAR"),
            ("photos_qty", "INTEGER"),
            ("weight_g", "DOUBLE"),
        ],
    )

    draw_table(
        0.5,
        0.6,
        3.2,
        2.3,
        "dim_customer",
        [
            ("PK customer_key", "INTEGER"),
            ("customer_id", "VARCHAR"),
            ("customer_unique_id", "VARCHAR"),
            ("zip_code_prefix", "INTEGER"),
            ("city, state", "VARCHAR"),
        ],
    )

    draw_table(
        8.3,
        0.6,
        3.2,
        2.3,
        "dim_seller",
        [
            ("PK seller_key", "INTEGER"),
            ("seller_id", "VARCHAR"),
            ("city, state", "VARCHAR"),
            ("tier", "VARCHAR"),
            ("handling_days", "INTEGER"),
        ],
    )

    draw_table(
        4.3,
        1.55,
        3.4,
        4.3,
        "fact_sales",
        [
            ("FK date_key", "INTEGER"),
            ("FK product_key", "INTEGER"),
            ("FK customer_key", "INTEGER"),
            ("FK seller_key", "INTEGER"),
            ("order_id", "VARCHAR"),
            ("order_item_id", "INTEGER"),
            ("order_status", "VARCHAR"),
            ("order_purchase_ts", "TIMESTAMP"),
            ("price", "DECIMAL(10,2)"),
            ("freight_value", "DECIMAL(10,2)"),
            ("total_item_value", "DECIMAL(10,2)"),
            ("quantity", "INTEGER"),
        ],
        header_bg="#D1FAE5",
    )

    ax.annotate("", xy=(4.28, 4.8), xytext=(3.72, 5.2), arrowprops=dict(arrowstyle="->", color="#4B5563", lw=1.3))
    ax.annotate("", xy=(7.72, 4.8), xytext=(8.28, 5.2), arrowprops=dict(arrowstyle="->", color="#4B5563", lw=1.3))
    ax.annotate("", xy=(4.28, 2.6), xytext=(3.72, 1.9), arrowprops=dict(arrowstyle="->", color="#4B5563", lw=1.3))
    ax.annotate("", xy=(7.72, 2.6), xytext=(8.28, 1.9), arrowprops=dict(arrowstyle="->", color="#4B5563", lw=1.3))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout(pad=0.25)
    plt.savefig(output_path, dpi=180, facecolor="#FFFFFF")
    plt.close(fig)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    ap2_root = Path(__file__).resolve().parent.parent
    create_pipeline_diagram(ap2_root / "architecture" / "pipeline_ap2.png")
    create_star_schema_diagram(ap2_root / "architecture" / "star_schema.png")
