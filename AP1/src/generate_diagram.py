#!/usr/bin/env python3
"""
Generate a high-resolution Star Schema Architecture diagram for NorthMart PA1.
Uses matplotlib to render a clean, professional dark-theme dimensional model.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def create_star_schema_diagram(output_path: str):
    fig, ax = plt.subplots(figsize=(16, 11), facecolor='#0D0E23')
    ax.set_facecolor('#0D0E23')
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11)
    ax.axis('off')

    # Palette
    c_bg = '#0D0E23'
    c_card = '#191A2F'
    c_header_fact = '#006A62'
    c_header_dim = '#1E3A5F'
    c_teal = '#81F3E5'
    c_white = '#FBF8FF'
    c_gray = '#A0A2C0'
    c_border = 'rgba(255, 255, 255, 0.1)'
    c_line = '#81F3E5'

    # Title
    ax.text(8, 10.5, "NorthMart Sales Star Schema Architecture", 
            fontsize=20, fontweight='bold', color=c_white, ha='center', va='center')
    ax.text(8, 10.1, "Granularity: One row per line item within an order | Fact Table with 4 Conformed Dimensions", 
            fontsize=11, color=c_teal, ha='center', va='center')

    # Helper function to draw table box
    def draw_table(x, y, w, h, title, columns, is_fact=False):
        header_h = 0.55
        header_color = c_header_fact if is_fact else c_header_dim
        
        # Main card body
        body = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.04,rounding_size=0.15",
            facecolor=c_card, edgecolor='#81F3E5' if is_fact else '#2D325A',
            linewidth=2 if is_fact else 1.2
        )
        ax.add_patch(body)

        # Header box
        header = patches.FancyBboxPatch(
            (x, y + h - header_h), w, header_h,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor=header_color, edgecolor='none'
        )
        ax.add_patch(header)

        # Title text
        ax.text(x + w/2, y + h - header_h/2, title,
                fontsize=11, fontweight='bold', color=c_white, ha='center', va='center')

        # Columns
        start_y = y + h - header_h - 0.25
        line_spacing = (h - header_h - 0.3) / max(len(columns), 1)
        for i, (col_name, col_type, is_key) in enumerate(columns):
            curr_y = start_y - (i * line_spacing)
            prefix = "[PK] " if "PK" in is_key else ("[FK] " if "FK" in is_key else ("[M]  " if "Measure" in is_key else "     "))
            key_color = c_teal if ("PK" in is_key or "FK" in is_key or "Measure" in is_key) else c_gray
            ax.text(x + 0.15, curr_y, f"{prefix}{col_name}", fontsize=8.5, 
                    fontweight='bold' if is_key else 'normal', color=c_white if is_key else '#D8D8E8', va='center')
            ax.text(x + w - 0.15, curr_y, col_type, fontsize=7.5, color=key_color, ha='right', va='center')

    # Fact Table (Center)
    fact_cols = [
        ("date_key", "INT (FK)", "FK"),
        ("product_key", "INT (FK)", "FK"),
        ("customer_key", "INT (FK)", "FK"),
        ("seller_key", "INT (FK)", "FK"),
        ("order_id", "VARCHAR (Degenerate)", ""),
        ("order_item_id", "INT (Degenerate)", ""),
        ("order_status", "VARCHAR (Degenerate)", ""),
        ("price", "DECIMAL(10,2) [Measure]", "Measure"),
        ("freight_value", "DECIMAL(10,2) [Measure]", "Measure"),
        ("total_item_value", "DECIMAL(10,2) [Measure]", "Measure"),
        ("quantity", "INT (Constant 1) [Measure]", "Measure"),
        ("year_month", "VARCHAR (Partition Key)", "")
    ]
    draw_table(6.0, 3.2, 4.0, 5.8, "fact_sales (Central Fact)", fact_cols, is_fact=True)

    # Dim Date (Top Left)
    date_cols = [
        ("date_key", "INT (PK: YYYYMMDD)", "PK"),
        ("date", "DATE", ""),
        ("year", "INT (2016-2018)", ""),
        ("month", "INT (1-12)", ""),
        ("quarter", "INT (1-4)", ""),
        ("day_of_week", "VARCHAR (Monday...)", ""),
        ("month_name", "VARCHAR (Jan...)", ""),
        ("year_month", "VARCHAR (YYYY-MM)", ""),
        ("is_weekend", "BOOLEAN", "")
    ]
    draw_table(0.8, 5.8, 3.8, 3.9, "dim_date (Time Dimension)", date_cols)

    # Dim Customer (Bottom Left)
    cust_cols = [
        ("customer_key", "INT (Surrogate PK)", "PK"),
        ("customer_id", "VARCHAR (Natural Key)", ""),
        ("customer_unique_id", "VARCHAR (Entity ID)", ""),
        ("zip_code_prefix", "INT", ""),
        ("city", "VARCHAR", ""),
        ("state", "VARCHAR (UF)", "")
    ]
    draw_table(0.8, 1.0, 3.8, 3.6, "dim_customer (Consumer)", cust_cols)

    # Dim Product (Top Right)
    prod_cols = [
        ("product_key", "INT (Surrogate PK)", "PK"),
        ("product_id", "VARCHAR (Natural Key)", ""),
        ("category_name", "VARCHAR (English)", ""),
        ("category_name_pt", "VARCHAR (Original)", ""),
        ("name_length", "INT", ""),
        ("description_length", "INT", ""),
        ("photos_qty", "INT", ""),
        ("weight_g", "DOUBLE", "")
    ]
    draw_table(11.4, 5.8, 3.8, 3.9, "dim_product (Item Catalog)", prod_cols)

    # Dim Seller (Bottom Right)
    seller_cols = [
        ("seller_key", "INT (Surrogate PK)", "PK"),
        ("seller_id", "VARCHAR (Natural Key)", ""),
        ("city", "VARCHAR", ""),
        ("state", "VARCHAR (UF)", ""),
        ("tier", "VARCHAR (Gold/Silver/Bronze)", ""),
        ("joined_on", "DATE", ""),
        ("handling_days", "INT (Dispatch SLA)", "")
    ]
    draw_table(11.4, 1.0, 3.8, 3.6, "dim_seller (Flattened JSON)", seller_cols)

    # Connector Lines (Star Schema Joins)
    # dim_date to fact
    ax.annotate("", xy=(6.0, 6.8), xytext=(4.6, 7.2),
                arrowprops=dict(arrowstyle="-|>", color=c_teal, lw=2, ls='-'))
    ax.text(5.2, 7.15, "1:N", fontsize=9, color=c_teal, fontweight='bold')

    # dim_customer to fact
    ax.annotate("", xy=(6.0, 4.8), xytext=(4.6, 3.2),
                arrowprops=dict(arrowstyle="-|>", color=c_teal, lw=2, ls='-'))
    ax.text(5.2, 4.15, "1:N", fontsize=9, color=c_teal, fontweight='bold')

    # dim_product to fact
    ax.annotate("", xy=(10.0, 6.8), xytext=(11.4, 7.2),
                arrowprops=dict(arrowstyle="-|>", color=c_teal, lw=2, ls='-'))
    ax.text(10.6, 7.15, "1:N", fontsize=9, color=c_teal, fontweight='bold')

    # dim_seller to fact
    ax.annotate("", xy=(10.0, 4.8), xytext=(11.4, 3.2),
                arrowprops=dict(arrowstyle="-|>", color=c_teal, lw=2, ls='-'))
    ax.text(10.6, 4.15, "1:N", fontsize=9, color=c_teal, fontweight='bold')

    # Footer note
    ax.text(8, 0.4, "All dimensions connect directly to fact_sales via integer surrogate keys. Zero Snowflake normalizations.",
            fontsize=9.5, color='#A0A2C0', ha='center', va='center', style='italic')

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Diagram successfully saved to {output_path}")

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out = os.path.join(base_dir, "architecture", "star_schema.png")
    create_star_schema_diagram(out)
