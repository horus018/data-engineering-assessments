# NorthMart AP1: Oral Defense Study Guide & Conceptual Mastery

> **Audience**: Students defending Practical Assessment 1 (PA1).  
> **Format**: Written individual exam / paper defense without laptops.  
> **Objective**: Master every architectural choice, technical term, and SQL transformation step.

---

## 1. Glossary of Core Data Engineering Keywords

| Keyword | Simple Definition | Why It Matters in PA1 |
| :--- | :--- | :--- |
| **OLTP (Transactional)** | Systems designed for fast, row-level operations (inserts, updates) with normalized schemas (3NF). | The source systems (PostgreSQL/e-commerce checkout) producing the raw CSV files. |
| **OLAP (Analytical)** | Systems designed to scan millions of rows across a few columns for aggregations (`SUM`, `AVG`, `GROUP BY`). | Our target analytical model in DuckDB and Parquet. |
| **Star Schema** | A dimensional data model consisting of a central fact table surrounded by denormalized dimension tables. | Resolves analyst complaints by eliminating complex multi-table joins. |
| **Fact Table** | A narrow, long table recording measurable events (transactions) with numeric measures and foreign keys. | `fact_sales` records order item events (112,650 rows). |
| **Dimension Table** | A wide, descriptive table providing contextual attributes (who, what, where, when, how). | `dim_date`, `dim_product`, `dim_customer`, `dim_seller`. |
| **Grain** | The exact atomic definition of what one single row represents. Stated in one sentence. | "One row per line item within an order placed on the NorthMart marketplace." |
| **Surrogate Key** | An artificial, meaningless integer primary key assigned by the data warehouse. | `product_key`, `customer_key`, `seller_key`, `date_key`. Insulates against natural key changes. |
| **Natural Key** | The original identifier created by the operational source system. | `product_id`, `customer_id`, `seller_id` (UUID strings). |
| **Degenerate Dimension** | A dimension attribute stored directly in the fact table without its own dimension table. | `order_id`, `order_item_id`, `order_status`. Avoids unnecessary join tables. |
| **Additive Measure** | A numerical metric that can be summed across every dimension (time, customer, product). | `price`, `freight_value`, `total_item_value`, `quantity`. |
| **Parquet** | A binary, columnar, compressed file storage format optimized for analytical queries. | Reduced storage from 121.4 MB to 3.49 MB (-97.1%). |
| **Partition Pruning** | An optimization where the query engine skips irrelevant file directories based on filters. | Queries on month `2018-05` skip 23 out of 24 folders, executing in ~3 ms. |
| **Lakehouse** | An architecture combining cheap, open file storage (Parquet) with ACID transactions and SQL engines. | The recommended architectural pattern for NorthMart. |
| **Data Swamp** | An unorganized data lake with no schema, no catalog, no data quality, and uncurated files. | What happens when raw files are queried directly without modeling. |
| **Idempotency** | The property where executing a pipeline multiple times produces the exact same state. | `build_model.sql` can be re-run safely at any time using `CREATE OR REPLACE` and `OVERWRITE TRUE`. |

---

## 2. Step-by-Step Breakdown of What We Built

### Step 1: Raw Data Profiling (`sql/profiling.sql`)
- **What we did**: We queried the 9 raw CSV files and the JSON file using DuckDB without altering source files.
- **Why we did it**: Before designing tables, a data engineer must inspect data reality—measuring row counts, key uniqueness, null percentages, and data defects.
- **Key discoveries**:
  1. **JSON Duplicates**: Found 3,095 total records for 3,070 unique sellers (25 duplicates with multiple `updated_at` dates).
  2. **JSON Dirty Data**: `profile.tier` had 9 different casing variants (`'Silver '`, `'SILVER'`, etc.) and 30 missing shipping records.
  3. **Seller Discrepancy**: 40 sellers in CSV were missing from JSON; 15 sellers in JSON were missing from CSV.
  4. **Product Catalog Nulls**: 610 products had `NULL` category names.
  5. **Order Delivery Nulls**: 2,965 orders lacked delivery dates because they were in-transit or canceled.

### Step 2: Dimensional Star Schema Design (`architecture/`)
- **What we did**: Designed 4 conformed dimensions around 1 central fact table.
- **Grain**: "One row per line item within an order placed on the NorthMart marketplace."
- **Dimensions**:
  - `dim_date`: Generated calendar dimension (2016–2018) with integer key `YYYYMMDD`.
  - `dim_product`: Translated Portuguese categories to English, imputed nulls to `'unknown'`.
  - `dim_customer`: Preserved order-level customer token (`customer_id`) and master customer (`customer_unique_id`).
  - `dim_seller`: Deduplicated JSON seller profiles, joined with CSV sellers, normalized tier to lowercase.
- **Non-Obvious Design Decision**:
  - Anchored `date_key` to `order_purchase_timestamp` (not delivery date) because 2,965 orders have no delivery date, and revenue occurs at purchase.
  - Kept `order_id` as a **degenerate dimension** inside `fact_sales` instead of creating a bloated `dim_order` table.

### Step 3: SQL Pipeline Implementation (`sql/build_model.sql`)
- **What we did**: Wrote pure DuckDB SQL transformations.
- **Surrogate Key Generation**: Used `ROW_NUMBER() OVER (ORDER BY natural_key)` to create integer keys.
- **JSON Deduplication**: Used window function `QUALIFY ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY updated_at DESC) = 1` to pick the latest profile snapshot.
- **Referential Integrity**: Implemented 4 SQL validation checks ensuring zero orphan foreign keys in `fact_sales`. All 112,650 order items joined with 100% integrity.

### Step 4: Parquet Storage & Performance Benchmarks (`sql/benchmark.sql`, `src/run_benchmark.py`)
- **What we did**: Exported `fact_sales` to:
  1. `fact_sales.parquet` (unpartitioned, ZSTD compression).
  2. `fact_sales_partitioned/` (partitioned by `year_month`, 24 folder partitions).
- **Benchmark Results**:
  - **Storage**: Raw files (121.4 MB) -> Parquet (3.49 MB) = **97.1% storage reduction**.
  - **Query 1 (All Months Revenue)**: CSV 190.65 ms -> Parquet Partitioned 8.14 ms (**23.4x faster**).
  - **Query 2 (Single Month 2018-05)**: CSV 171.30 ms -> Parquet Partitioned 3.07 ms (**55.8x faster** via partition pruning).
  - **Query 3 (Top 5 Categories)**: CSV 135.20 ms -> Parquet Partitioned 12.08 ms (**11.2x faster**).

### Step 5: Architectural Choice (Lakehouse)
- **What we did**: Evaluated Warehouse vs Lake vs Lakehouse.
- **Conclusion**: A **Lakehouse** is optimal for NorthMart:
  - Avoids high SaaS costs of proprietary data warehouses.
  - Avoids the governance collapse ("data swamp") of plain data lakes.
  - Provides open-standard Parquet files with ACID metadata and ultra-fast vectorized SQL querying.

---

## 3. High-Yield Oral Defense Questions & Model Answers

### Q1: Why do we use surrogate keys instead of natural keys?
**Model Answer**:  
"Natural keys come from source systems that we do not control; they can change format, collide during mergers, or contain long strings (UUIDs) that slow down joins. Surrogate keys are sequential integers managed by the warehouse. They ensure faster integer joins, insulate our analytical model from upstream changes, and are mandatory for implementing Slowly Changing Dimensions (SCD Type 2)."

### Q2: What is the grain of your fact table, and why is declaring it first so important?
**Model Answer**:  
"Our grain is: *One row per line item within an order placed on the NorthMart marketplace.* Declaring the grain first is Kimball’s golden rule because every measure and foreign key depends on it. If you mix grains (for example, combining order-level totals with item-level lines), aggregations will double-count revenue."

### Q3: Why is Parquet so much faster than CSV for analytical queries?
**Model Answer**:  
"Parquet is columnar and binary, whereas CSV is row-oriented text. In our analytical queries (such as calculating monthly revenue), we only need the `price` and `date_key` columns. Parquet reads only the bytes belonging to those specific columns (**column pruning**), skipping the remaining columns entirely. Furthermore, Parquet stores pre-computed statistics in file footers and requires zero text parsing."

### Q4: What is partition pruning, and which query demonstrated it?
**Model Answer**:  
"Partition pruning is when the query engine uses file path metadata to skip directories that cannot match the query filter. In Query 2 (`WHERE year_month = '2018-05'`), DuckDB skipped 23 out of 24 monthly partition folders, scanning only the relevant month. This reduced execution time from 171.30 ms in CSV down to 3.07 ms in partitioned Parquet."

### Q5: What defects did you find in the seller JSON file, and how did you resolve them?
**Model Answer**:  
"We found 25 duplicate records with conflicting `updated_at` dates, 9 inconsistent casing variants in `profile.tier` (like `'Silver '` and `'SILVER'`), and 30 records missing shipping data. We resolved them in DuckDB SQL using `QUALIFY ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY updated_at DESC) = 1` to take the latest profile, applied `LOWER(TRIM(profile.tier))`, and filled missing shipping values with defaults."

### Q6: Why did you keep `order_id` in the fact table instead of creating `dim_order`?
**Model Answer**:  
"This is a Kimball design pattern called a **degenerate dimension**. `order_id` is an operational transaction identifier that has no descriptive attributes beyond what is already in our dimensions. Creating a separate `dim_order` table would introduce an unnecessary join for every report. Storing it directly in the fact table provides full transaction traceability with zero join cost."

### Q7: Why did you choose a Lakehouse over a traditional Data Warehouse?
**Model Answer**:  
"A traditional cloud warehouse couples storage and compute or charges high proprietary storage fees. For NorthMart’s volume (112,650 rows, 3.49 MB Parquet), an expensive warehouse is overkill. A lakehouse stores data in open, vendor-neutral Parquet files while enabling ACID transactions and fast embedded query engines like DuckDB, cutting storage by 97.1% and latency by over 50x without proprietary lock-in."

### Q8: What makes a measure 'additive', and what measures did you include?
**Model Answer**:  
"An additive measure is a numeric value that can be meaningfully summed across all dimensions. We included `price`, `freight_value`, `total_item_value`, and a constant `quantity = 1`. Ratios and percentages (like profit margins) are non-additive and must never be pre-aggregated in fact tables; they should be computed dynamically at query time from additive numerators and denominators."

### Q9: What are the risks of a plain Data Lake, and how does Lakehouse prevent them?
**Model Answer**:  
"A plain data lake uses schema-on-read with no enforced schema, no transaction guarantees, and no catalog. It easily degenerates into a 'data swamp' where nobody knows what files exist and concurrent writes produce corrupted data. A lakehouse adds a metadata/transaction layer that guarantees ACID transactions, schema enforcement, and time travel over open files."

### Q10: How did you ensure your data pipeline is idempotent?
**Model Answer**:  
"An idempotent pipeline produces the exact same result whether executed once or ten times. We achieved idempotency by using `CREATE OR REPLACE TABLE` in DuckDB and `OVERWRITE TRUE` on Parquet export statements, completely replacing output tables and files rather than blindly appending rows."
