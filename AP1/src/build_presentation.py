#!/usr/bin/env python3
"""
Generate a professional, publication-quality 16:9 widescreen presentation
for NorthMart PA1 Defense in PPTX format, and convert to PDF via LibreOffice.
Theme: WorkFlow Dark Theme (#0D0E23, #191A2F, #006A62, #81F3E5, #FBF8FF)
"""

import os
import subprocess
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def hex_to_rgb(hex_str: str) -> RGBColor:
    hex_str = hex_str.lstrip('#')
    return RGBColor(*(int(hex_str[i:i+2], 16) for i in (0, 2, 4)))

# Theme Colors
C_BG = hex_to_rgb('0D0E23')       # Deep Navy
C_CARD = hex_to_rgb('191A2F')     # Card Secondary Navy
C_PRIMARY = hex_to_rgb('006A62')  # Petroleum Green Accent
C_TEAL = hex_to_rgb('81F3E5')     # Aqua Teal Highlight
C_WHITE = hex_to_rgb('FBF8FF')    # Soft White
C_MUTED = hex_to_rgb('A0A2C0')    # Muted Slate Gray
C_BORDER = hex_to_rgb('2D325A')   # Border Outline

def add_header(slide, title_text: str, subtitle_text: str = ""):
    # Title
    tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.8))
    tf = tx_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.font.name = 'Arial'

    if subtitle_text:
        p2 = tf.add_paragraph()
        p2.text = subtitle_text
        p2.font.size = Pt(13)
        p2.font.color.rgb = C_TEAL
        p2.font.name = 'Arial'

def create_card(slide, left, top, width, height, bg_color=C_CARD, border_color=C_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.5)
    return shape

def build_presentation(output_pptx: str):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def base_slide():
        slide = prs.slides.add_slide(blank_layout)
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background()
        return slide

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1 = base_slide()
    create_card(s1, Inches(1.2), Inches(1.2), Inches(10.933), Inches(5.1), bg_color=C_CARD, border_color=C_TEAL)
    
    t_box = s1.shapes.add_textbox(Inches(1.6), Inches(1.8), Inches(10.133), Inches(3.8))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "NorthMart Analytical Data Platform"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    
    p2 = tf1.add_paragraph()
    p2.text = "PA1: From Raw Files to a Kimball Star Schema in DuckDB & Parquet"
    p2.font.size = Pt(18)
    p2.font.bold = True
    p2.font.color.rgb = C_TEAL
    p2.space_before = Pt(14)
    
    p3 = tf1.add_paragraph()
    p3.text = "Data Engineering (2026/2027) | Instituto Politécnico de Bragança (IPB / UPB)\nOral Defense & System Implementation Review"
    p3.font.size = Pt(13)
    p3.font.color.rgb = C_MUTED
    p3.space_before = Pt(28)

    # ==========================================
    # SLIDE 2: Business Scenario & Pain Points
    # ==========================================
    s2 = base_slide()
    add_header(s2, "Business Scenario & Analytical Bottlenecks", "Why NorthMart needed a dedicated dimensional layer")
    
    create_card(s2, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2))
    t1 = s2.shapes.add_textbox(Inches(1.1), Inches(1.7), Inches(5.0), Inches(4.7)).text_frame
    t1.word_wrap = True
    p = t1.paragraphs[0]
    p.text = "The Operational Problem (As-Is)"
    p.font.size = Pt(18); p.font.bold = True; p.font.color.rgb = C_TEAL
    
    items = [
        ("Disorganized Data Islands", "Analysts queried 9 separate CSV exports (~121 MB) and a nested JSON file directly."),
        ("Slow, Wasteful Scans", "Queries parsed raw CSV text on every run, repeating disk reads and type inference."),
        ("Inconsistent Joins", "Different analysts joined tables differently, producing conflicting KPI reports."),
        ("Dirty Operational Feeds", "JSON exports contained temporal duplicate seller profiles, missing SLA fields, and malformed casings.")
    ]
    for title, desc in items:
        p = t1.add_paragraph()
        p.text = f"• {title}: "
        p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_WHITE; p.space_before = Pt(12)
        p_sub = t1.add_paragraph()
        p_sub.text = f"   {desc}"
        p_sub.font.size = Pt(11); p_sub.font.color.rgb = C_MUTED

    create_card(s2, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.2))
    t2 = s2.shapes.add_textbox(Inches(7.2), Inches(1.7), Inches(5.0), Inches(4.7)).text_frame
    t2.word_wrap = True
    p = t2.paragraphs[0]
    p.text = "The Engineering Solution (To-Be)"
    p.font.size = Pt(18); p.font.bold = True; p.font.color.rgb = C_TEAL
    
    sol_items = [
        ("Kimball Dimensional Star Schema", "Single conformed fact table at order-item grain surrounded by 4 clean dimensions."),
        ("Embedded DuckDB Engine", "Vectorized in-memory SQL execution eliminating heavyweight cluster overhead."),
        ("Curated Parquet Storage", "Columnar compression reducing disk footprint by 97.1% with partition pruning."),
        ("Automated Quality Gates", "Surrogate keys and referential integrity assertions ensuring zero orphaned records.")
    ]
    for title, desc in sol_items:
        p = t2.add_paragraph()
        p.text = f"✔ {title}: "
        p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_WHITE; p.space_before = Pt(12)
        p_sub = t2.add_paragraph()
        p_sub.text = f"   {desc}"
        p_sub.font.size = Pt(11); p_sub.font.color.rgb = C_MUTED

    # ==========================================
    # SLIDE 3: Task 1 - Raw Profiling Findings
    # ==========================================
    s3 = base_slide()
    add_header(s3, "Task 1: Raw Data Profiling & Empirical Findings", "Conducted in DuckDB over 121.4 MB of raw CSVs and JSON")

    findings = [
        ("Finding 1: JSON Duplication (25 Duplicates)", "The JSON export has 3,095 rows but only 3,070 unique sellers. Multiple records represent state updates over time (e.g. seller dc120d93... updated in 2017 and 2018).", C_TEAL),
        ("Finding 2: Dirty JSON Tiers & Null SLA", "profile.tier contains 9 distinct raw casing variants ('Silver ', 'SILVER', 'silver'). 30 sellers (0.97%) have completely null shipping objects.", C_TEAL),
        ("Finding 3: CSV vs JSON Seller Discrepancies", "40 sellers in the CSV master are absent from the JSON export; 15 sellers in JSON are absent from CSV orders. Required LEFT JOIN with conformed defaults.", C_WHITE),
        ("Finding 4: Order Granularity & Lifecycle Nulls", "99,441 orders generate 112,650 order items (1:N, max 21 items/order). 2,965 orders (2.98%) lack customer delivery dates (in-transit/cancelled).", C_WHITE),
        ("Finding 5: Catalog Nulls & Missing Translations", "610 products have null category names; 2 Portuguese categories lack English translations. Resolved via Kimball 'unknown' imputation.", C_WHITE)
    ]
    card_w = Inches(11.733)
    card_h = Inches(0.92)
    start_top = Inches(1.5)
    
    for i, (f_title, f_desc, color) in enumerate(findings):
        top_pos = start_top + Inches(i * 1.05)
        create_card(s3, Inches(0.8), top_pos, card_w, card_h)
        tf = s3.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.08), card_w - Inches(0.4), card_h - Inches(0.16)).text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f_title
        p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = color
        p2 = tf.add_paragraph()
        p2.text = f_desc
        p2.font.size = Pt(11); p2.font.color.rgb = C_MUTED

    # ==========================================
    # SLIDE 4: Task 2 - Star Schema Architecture
    # ==========================================
    s4 = base_slide()
    add_header(s4, "Task 2: Kimball Star Schema Architecture", "Single fact table, conformed dimensions, and explicit grain declaration")

    # Left: Architecture details
    create_card(s4, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
    tf = s4.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.2), Inches(4.9)).text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Core Architectural Specifications"
    p.font.size = Pt(18); p.font.bold = True; p.font.color.rgb = C_TEAL

    p = tf.add_paragraph()
    p.text = "1. Declared Grain (Kimball Rule):"
    p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_WHITE; p.space_before = Pt(10)
    p2 = tf.add_paragraph()
    p2.text = "   \"One row per line item within an order placed on the NorthMart marketplace.\""
    p2.font.size = Pt(11); p2.font.color.rgb = C_TEAL; p2.font.italic = True

    p = tf.add_paragraph()
    p.text = "2. Fully Additive Measures:"
    p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_WHITE; p.space_before = Pt(10)
    p2 = tf.add_paragraph()
    p2.text = "   • price, freight_value, total_item_value, quantity (constant 1)"
    p2.font.size = Pt(11); p2.font.color.rgb = C_MUTED

    p = tf.add_paragraph()
    p.text = "3. Non-Obvious Modelling Decisions:"
    p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_WHITE; p.space_before = Pt(10)
    p2 = tf.add_paragraph()
    p2.text = "   • Primary Date: Anchored to order purchase date (not delivery date, which has 2,965 nulls).\n   • Degenerate Dimension: order_id kept in fact table to eliminate unnecessary join tables."
    p2.font.size = Pt(11); p2.font.color.rgb = C_MUTED

    # Right: Schema Diagram Image
    create_card(s4, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.3))
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    diagram_img = os.path.join(base_dir, "architecture", "star_schema.png")
    if os.path.exists(diagram_img):
        s4.shapes.add_picture(diagram_img, Inches(7.0), Inches(1.7), width=Inches(5.3))

    # ==========================================
    # SLIDE 5: Task 3 - DuckDB Pipeline & Integrity
    # ==========================================
    s5 = base_slide()
    add_header(s5, "Task 3: Pipeline Implementation & Quality Gates", "Pure SQL transformation pipeline in DuckDB with zero-orphan referential checks")

    create_card(s5, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2))
    tf = s5.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.2), Inches(4.7)).text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Dimensional ETL Highlights"
    p.font.size = Pt(18); p.font.bold = True; p.font.color.rgb = C_TEAL

    highlights = [
        ("Surrogate Keys", "Deterministic integer keys generated with ROW_NUMBER() OVER (ORDER BY natural_key). Insulates analytical schema from upstream source system key changes."),
        ("JSON Flattening & Deduplication", "Extracted nested structs via dot-notation. Deduplicated sellers with QUALIFY ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY updated_at DESC) = 1."),
        ("Catalog Enrichment", "Joined Portuguese catalog with English translations; mapped null categories to 'unknown'."),
        ("Preserved Fact Granularity", "Exactly 112,650 order items loaded into fact_sales (100% data preservation).")
    ]
    for h_title, h_desc in highlights:
        p = tf.add_paragraph()
        p.text = f"• {h_title}:"
        p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = C_WHITE; p.space_before = Pt(8)
        p2 = tf.add_paragraph()
        p2.text = f"   {h_desc}"
        p2.font.size = Pt(10.5); p2.font.color.rgb = C_MUTED

    # Right: Automated Referential Integrity Results
    create_card(s5, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2))
    tf = s5.shapes.add_textbox(Inches(7.1), Inches(1.7), Inches(5.1), Inches(4.7)).text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Referential Integrity Validation"
    p.font.size = Pt(18); p.font.bold = True; p.font.color.rgb = C_TEAL

    checks = [
        ("fact_sales -> dim_date", "0 Orphaned Keys", "PASSED"),
        ("fact_sales -> dim_product", "0 Orphaned Keys", "PASSED"),
        ("fact_sales -> dim_customer", "0 Orphaned Keys", "PASSED"),
        ("fact_sales -> dim_seller", "0 Orphaned Keys", "PASSED"),
        ("Price / Freight Measures", "No Negative Values", "PASSED"),
        ("Grain Uniqueness Check", "0 Key Collisions", "PASSED")
    ]
    for rel, detail, status in checks:
        p = tf.add_paragraph()
        p.text = f"✔ {rel}: {detail} [{status}]"
        p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = C_WHITE; p.space_before = Pt(10)

    # ==========================================
    # SLIDE 6: Task 4 - Benchmarks & Measurements
    # ==========================================
    s6 = base_slide()
    add_header(s6, "Task 4: Storage Footprints & Performance Benchmarks", "Empirical measurement across CSV vs Parquet Unpartitioned vs Parquet Partitioned")

    # Card 1: Storage
    create_card(s6, Inches(0.8), Inches(1.5), Inches(11.733), Inches(2.4))
    tf = s6.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(11.3), Inches(2.2)).text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Storage Footprint Comparison"
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = C_TEAL

    p = tf.add_paragraph()
    p.text = "• Full Raw Source (9 CSVs + 1 JSON): 121.40 MB (Baseline)\n• Curated Parquet Unpartitioned (fact_sales.parquet): 3.49 MB  -->  97.1% Storage Reduction\n• Curated Parquet Partitioned (24 Month Directories): 3.63 MB  -->  97.0% Storage Reduction"
    p.font.size = Pt(12); p.font.color.rgb = C_WHITE; p.space_before = Pt(8)

    # Card 2: Query Execution Latency Table
    create_card(s6, Inches(0.8), Inches(4.1), Inches(11.733), Inches(2.8))
    tf = s6.shapes.add_textbox(Inches(1.0), Inches(4.2), Inches(11.3), Inches(2.6)).text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. Query Execution Latency (Average of 5 Runs in DuckDB)"
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = C_TEAL

    p = tf.add_paragraph()
    p.text = "• Query 1 (Monthly Revenue Over Whole Period):\n   CSV: 190.65 ms  |  Parquet: 11.02 ms  |  Partitioned: 8.14 ms  -->  23.4x Faster\n• Query 2 (Single Month Revenue & Items - 2018-05):\n   CSV: 171.30 ms  |  Parquet: 6.94 ms   |  Partitioned: 3.07 ms  -->  55.8x Faster (Partition Pruning)\n• Query 3 (Top 5 Product Categories by Revenue):\n   CSV: 135.20 ms  |  Parquet: 15.46 ms  |  Partitioned: 12.08 ms  -->  11.2x Faster"
    p.font.size = Pt(11); p.font.color.rgb = C_WHITE; p.space_before = Pt(6)

    # ==========================================
    # SLIDE 7: Task 5 - Lakehouse Architectural Choice
    # ==========================================
    s7 = base_slide()
    add_header(s7, "Task 5: Architectural Justification (Warehouse vs Lake vs Lakehouse)", "NorthMart is best served by a Lakehouse architecture")

    create_card(s7, Inches(0.8), Inches(1.5), Inches(3.6), Inches(5.2))
    tf = s7.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(3.2), Inches(4.7)).text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Data Warehouse"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = hex_to_rgb('FFB4AB')
    p = tf.add_paragraph()
    p.text = "❌ Excessive Cost\nProprietary storage and compute licensing (Snowflake, BigQuery) is wasteful for 112k rows.\n\n❌ Rigid Schemas\nSlow to adapt to new unstructured feeds."
    p.font.size = Pt(11); p.font.color.rgb = C_MUTED; p.space_before = Pt(10)

    create_card(s7, Inches(4.8), Inches(1.5), Inches(3.6), Inches(5.2))
    tf = s7.shapes.add_textbox(Inches(5.0), Inches(1.7), Inches(3.2), Inches(4.7)).text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Data Lake"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = hex_to_rgb('FFB4AB')
    p = tf.add_paragraph()
    p.text = "❌ Becomes a 'Data Swamp'\nNo schema enforcement, no ACID transactions, and no table catalogue.\n\n❌ Unreliable Reports\nConcurrent writes cause corrupt reads and divergent joins."
    p.font.size = Pt(11); p.font.color.rgb = C_MUTED; p.space_before = Pt(10)

    create_card(s7, Inches(8.8), Inches(1.5), Inches(3.7), Inches(5.2), border_color=C_TEAL)
    tf = s7.shapes.add_textbox(Inches(9.0), Inches(1.7), Inches(3.3), Inches(4.7)).text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = "Data Lakehouse"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = C_TEAL
    p = tf.add_paragraph()
    p.text = "✔ Fact 1: 97.1% Storage Saving\nParquet reduces 121.4 MB raw CSV to 3.49 MB open storage.\n\n✔ Fact 2: 55.8x Latency Drop\nSingle-month queries drop from 171 ms to 3.07 ms via partition pruning.\n\n✔ ACID & Interoperability\nOpen files with zero SaaS vendor lock-in."
    p.font.size = Pt(11); p.font.color.rgb = C_WHITE; p.space_before = Pt(10)

    # ==========================================
    # SLIDE 8: Oral Defense Keywords Cheat Sheet
    # ==========================================
    s8 = base_slide()
    add_header(s8, "Oral Defense Conceptual Cheat Sheet", "Essential concepts required for individual examination")

    cards = [
        ("Surrogate Keys", "Integer keys created by the warehouse. Faster joins, isolates schema from operational changes, enables SCD Type 2."),
        ("Grain Declaration", "The single sentence defining what 1 row is. Must be declared first to prevent incorrect aggregations."),
        ("Degenerate Dimension", "Dimension attribute kept in the fact table without its own table (order_id). Avoids unnecessary joins."),
        ("Partition Pruning", "Query engine skips irrelevant directories using file metadata. Q2 skips 23/24 month partitions in 3 ms."),
        ("Columnar Storage", "Parquet reads only queried columns and skips unneeded ones. Drastically reduces I/O compared to CSV."),
        ("Idempotency", "Pipeline can run repeatedly producing the identical clean state (CREATE OR REPLACE, OVERWRITE TRUE).")
    ]
    
    for idx, (term, definition) in enumerate(cards):
        row = idx // 2
        col = idx % 2
        x = Inches(0.8 + col * 5.95)
        y = Inches(1.5 + row * 1.75)
        create_card(s8, x, y, Inches(5.75), Inches(1.55))
        tf = s8.shapes.add_textbox(x + Inches(0.2), y + Inches(0.12), Inches(5.35), Inches(1.3)).text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = term
        p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = C_TEAL
        p2 = tf.add_paragraph()
        p2.text = definition
        p2.font.size = Pt(10.5); p2.font.color.rgb = C_MUTED; p2.space_before = Pt(4)

    # ==========================================
    # SLIDE 9: Conclusion & Execution Commands
    # ==========================================
    s9 = base_slide()
    add_header(s9, "Summary & Reproduction Commands", "Everything runs deterministically from the repository")

    create_card(s9, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.2))
    tf = s9.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(10.9), Inches(4.5)).text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Commands to Reproduce the Full Evaluation"
    p.font.size = Pt(20); p.font.bold = True; p.font.color.rgb = C_TEAL

    cmds = [
        ("Step 1 - Profile Raw Files", "duckdb < sql/profiling.sql"),
        ("Step 2 - Build Star Schema & Curated Parquet", "duckdb northmart.duckdb < sql/build_model.sql"),
        ("Step 3 - Run Benchmark Suite", "python3 src/run_benchmark.py"),
        ("Step 4 - Run Automated Quality Tests", "python3 tests/run_tests.py")
    ]
    for step_title, cmd in cmds:
        p = tf.add_paragraph()
        p.text = f"{step_title}:"
        p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = C_WHITE; p.space_before = Pt(12)
        p2 = tf.add_paragraph()
        p2.text = f"   $ {cmd}"
        p2.font.size = Pt(12); p2.font.color.rgb = C_TEAL; p2.font.name = 'Courier New'

    # Save PPTX
    prs.save(output_pptx)
    print(f"Presentation saved successfully to {output_pptx}")

    # Convert to PDF via LibreOffice
    output_dir = os.path.dirname(output_pptx)
    pdf_cmd = f"libreoffice --headless --convert-to pdf '{output_pptx}' --outdir '{output_dir}'"
    print(f"Converting to PDF: {pdf_cmd}")
    subprocess.run(pdf_cmd, shell=True, check=True)
    pdf_path = os.path.splitext(output_pptx)[0] + ".pdf"
    print(f"PDF successfully generated at {pdf_path}")

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pptx_path = os.path.join(base_dir, "presentation.pptx")
    build_presentation(pptx_path)
