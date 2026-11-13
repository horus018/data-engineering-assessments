-- ============================================================================
-- NorthMart Data Platform - PA1 Task 3: Dimensional Model Build
-- Engine: DuckDB
-- Description: Builds the Kimball star schema from raw CSV and JSON files.
-- Features:
--   - Generated calendar dimension (dim_date)
--   - Translated and cleaned product dimension (dim_product)
--   - Granular customer dimension with unique entity tracking (dim_customer)
--   - Deduplicated and flattened seller JSON profiles (dim_seller)
--   - Central fact table at order-item grain (fact_sales)
--   - Surrogate keys across all dimensions
--   - Automated referential integrity validation checks
--   - Exports fact table to unpartitioned and partitioned Parquet layouts
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Create Source Views
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW raw_orders AS 
SELECT * FROM read_csv_auto('data/source/olist_orders_dataset.csv');

CREATE OR REPLACE VIEW raw_order_items AS 
SELECT * FROM read_csv_auto('data/source/olist_order_items_dataset.csv');

CREATE OR REPLACE VIEW raw_products AS 
SELECT * FROM read_csv_auto('data/source/olist_products_dataset.csv');

CREATE OR REPLACE VIEW raw_customers AS 
SELECT * FROM read_csv_auto('data/source/olist_customers_dataset.csv');

CREATE OR REPLACE VIEW raw_sellers AS 
SELECT * FROM read_csv_auto('data/source/olist_sellers_dataset.csv');

CREATE OR REPLACE VIEW raw_category_translation AS 
SELECT * FROM read_csv_auto('data/source/product_category_name_translation.csv');

CREATE OR REPLACE VIEW raw_sellers_json AS 
SELECT * FROM read_json_auto('data/source/northmart_seller_profiles.json');


-- ----------------------------------------------------------------------------
-- 2. Build Dimension Tables
-- ----------------------------------------------------------------------------

-- 2.1 Date Dimension (dim_date)
-- Spans full order history range from 2016 to 2018 with rich calendar attributes
CREATE OR REPLACE TABLE dim_date AS
SELECT
    CAST(strftime(d, '%Y%m%d') AS INTEGER) AS date_key,
    CAST(d AS DATE) AS date,
    year(d) AS year,
    month(d) AS month,
    quarter(d) AS quarter,
    day(d) AS day,
    dayname(d) AS day_of_week,
    monthname(d) AS month_name,
    strftime(d, '%Y-%m') AS year_month,
    isodow(d) >= 6 AS is_weekend
FROM range(DATE '2016-01-01', DATE '2019-01-01', INTERVAL 1 DAY) t(d);


-- 2.2 Product Dimension (dim_product)
-- Joins category translation, normalizes null categories to 'unknown'
CREATE OR REPLACE TABLE dim_product AS
SELECT
    ROW_NUMBER() OVER (ORDER BY p.product_id) AS product_key,
    p.product_id,
    COALESCE(p.product_category_name, 'unknown') AS category_name_pt,
    COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category_name,
    COALESCE(p.product_name_lenght, 0) AS name_length,
    COALESCE(p.product_description_lenght, 0) AS description_length,
    COALESCE(p.product_photos_qty, 0) AS photos_qty,
    COALESCE(p.product_weight_g, 0.0) AS weight_g,
    COALESCE(p.product_length_cm, 0.0) AS length_cm,
    COALESCE(p.product_height_cm, 0.0) AS height_cm,
    COALESCE(p.product_width_cm, 0.0) AS width_cm
FROM raw_products p
LEFT JOIN raw_category_translation t ON p.product_category_name = t.product_category_name;


-- 2.3 Customer Dimension (dim_customer)
CREATE OR REPLACE TABLE dim_customer AS
SELECT
    ROW_NUMBER() OVER (ORDER BY c.customer_id) AS customer_key,
    c.customer_id,
    c.customer_unique_id,
    COALESCE(c.customer_zip_code_prefix, 'unknown') AS zip_code_prefix,
    COALESCE(c.customer_city, 'unknown') AS city,
    COALESCE(c.customer_state, 'unknown') AS state
FROM raw_customers c;


-- 2.4 Seller Dimension (dim_seller)
-- Deduplicates JSON profiles keeping latest updated_at record.
-- Normalizes casing and whitespace on tier.
-- Uses LEFT JOIN from master sellers table to ensure zero loss of referential integrity.
CREATE OR REPLACE TABLE dim_seller AS
SELECT
    ROW_NUMBER() OVER (ORDER BY s.seller_id) AS seller_key,
    s.seller_id,
    COALESCE(s.seller_zip_code_prefix, 'unknown') AS zip_code_prefix,
    COALESCE(s.seller_city, 'unknown') AS city,
    COALESCE(s.seller_state, 'unknown') AS state,
    COALESCE(j.tier, 'unknown') AS tier,
    j.joined_on,
    COALESCE(j.handling_days, -1) AS handling_days
FROM raw_sellers s
LEFT JOIN (
    SELECT 
        seller_id,
        LOWER(TRIM(profile.tier)) AS tier,
        profile.joined_on AS joined_on,
        shipping.handling_days AS handling_days
    FROM raw_sellers_json
    QUALIFY ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY updated_at DESC) = 1
) j ON s.seller_id = j.seller_id;


-- ----------------------------------------------------------------------------
-- 3. Build Fact Table (fact_sales)
-- Grain: One row per line item within an order placed on NorthMart marketplace
-- ----------------------------------------------------------------------------
CREATE OR REPLACE TABLE fact_sales AS
SELECT
    CAST(strftime(o.order_purchase_timestamp, '%Y%m%d') AS INTEGER) AS date_key,
    strftime(o.order_purchase_timestamp, '%Y-%m') AS year_month,
    p.product_key,
    c.customer_key,
    s.seller_key,
    oi.order_id,
    oi.order_item_id,
    o.order_status,
    ROUND(CAST(oi.price AS DOUBLE), 2) AS price,
    ROUND(CAST(oi.freight_value AS DOUBLE), 2) AS freight_value,
    ROUND(CAST(oi.price + oi.freight_value AS DOUBLE), 2) AS total_item_value,
    1 AS quantity
FROM raw_order_items oi
JOIN raw_orders o ON oi.order_id = o.order_id
JOIN dim_product p ON oi.product_id = p.product_id
JOIN dim_customer c ON o.customer_id = c.customer_id
JOIN dim_seller s ON oi.seller_id = s.seller_id;


-- ----------------------------------------------------------------------------
-- 4. Automated Referential Integrity Checks
-- ----------------------------------------------------------------------------
SELECT '=== REFERENTIAL INTEGRITY CHECKS (MUST BE 0 VIOLATIONS) ===' AS check_status;

SELECT 
    'fact_sales -> dim_date' AS fk_relationship,
    COUNT(*) AS orphaned_records,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS result
FROM fact_sales f
LEFT JOIN dim_date d ON f.date_key = d.date_key
WHERE d.date_key IS NULL

UNION ALL

SELECT 
    'fact_sales -> dim_product',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM fact_sales f
LEFT JOIN dim_product p ON f.product_key = p.product_key
WHERE p.product_key IS NULL

UNION ALL

SELECT 
    'fact_sales -> dim_customer',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM fact_sales f
LEFT JOIN dim_customer c ON f.customer_key = c.customer_key
WHERE c.customer_key IS NULL

UNION ALL

SELECT 
    'fact_sales -> dim_seller',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM fact_sales f
LEFT JOIN dim_seller s ON f.seller_key = s.seller_key
WHERE s.seller_key IS NULL;


-- ----------------------------------------------------------------------------
-- 5. Export Fact Table to Parquet Layouts (Task 4 Curated Storage)
-- ----------------------------------------------------------------------------
SELECT '=== EXPORTING CURATED PARQUET LAYOUTS ===' AS export_status;

-- 5.1 Export Unpartitioned Parquet
COPY fact_sales TO 'data/curated/fact_sales.parquet' 
(FORMAT PARQUET, COMPRESSION ZSTD, OVERWRITE TRUE);

-- 5.2 Export Partitioned Parquet (by year_month)
COPY fact_sales TO 'data/curated/fact_sales_partitioned' 
(FORMAT PARQUET, PARTITION_BY (year_month), COMPRESSION ZSTD, OVERWRITE TRUE);

SELECT 'Model build, validation and Parquet exports completed successfully.' AS status;
