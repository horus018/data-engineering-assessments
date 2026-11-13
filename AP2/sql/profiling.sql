-- ============================================================================
-- NorthMart Data Platform - PA1 Task 1: Raw Data Profiling
-- Engine: DuckDB
-- Description: Comprehensive profiling of raw CSV exports and JSON seller profiles.
-- Evaluates row counts, primary key uniqueness, null rates, duplicate records,
-- and cross-dataset referential integrity.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Create Views Over Raw Source Files
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

CREATE OR REPLACE VIEW raw_payments AS 
SELECT * FROM read_csv_auto('data/source/olist_order_payments_dataset.csv');

CREATE OR REPLACE VIEW raw_reviews AS 
SELECT * FROM read_csv_auto('data/source/olist_order_reviews_dataset.csv');

CREATE OR REPLACE VIEW raw_geolocation AS 
SELECT * FROM read_csv_auto('data/source/olist_geolocation_dataset.csv');

CREATE OR REPLACE VIEW raw_category_translation AS 
SELECT * FROM read_csv_auto('data/source/product_category_name_translation.csv');

CREATE OR REPLACE VIEW raw_sellers_json AS 
SELECT * FROM read_json_auto('data/source/northmart_seller_profiles.json');


-- ----------------------------------------------------------------------------
-- 2. Global Dataset Row Counts
-- ----------------------------------------------------------------------------
SELECT '=== 1. GLOBAL ROW COUNTS ===' AS section;

SELECT 'orders' AS dataset, COUNT(*) AS row_count FROM raw_orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM raw_order_items
UNION ALL
SELECT 'products', COUNT(*) FROM raw_products
UNION ALL
SELECT 'customers', COUNT(*) FROM raw_customers
UNION ALL
SELECT 'sellers (csv)', COUNT(*) FROM raw_sellers
UNION ALL
SELECT 'sellers (json)', COUNT(*) FROM raw_sellers_json
UNION ALL
SELECT 'order_payments', COUNT(*) FROM raw_payments
UNION ALL
SELECT 'order_reviews', COUNT(*) FROM raw_reviews
UNION ALL
SELECT 'geolocation', COUNT(*) FROM raw_geolocation
UNION ALL
SELECT 'category_translation', COUNT(*) FROM raw_category_translation;


-- ----------------------------------------------------------------------------
-- 3. Primary Key Uniqueness and Duplicate Checks
-- ----------------------------------------------------------------------------
SELECT '=== 2. PRIMARY KEY UNIQUENESS & DUPLICATE CHECKS ===' AS section;

SELECT 
    'orders' AS entity,
    'order_id' AS key_column,
    COUNT(*) AS total_rows,
    COUNT(DISTINCT order_id) AS distinct_keys,
    COUNT(*) - COUNT(DISTINCT order_id) AS duplicate_count
FROM raw_orders
UNION ALL
SELECT 
    'order_items',
    'order_id || _ || order_item_id',
    COUNT(*),
    COUNT(DISTINCT order_id || '_' || CAST(order_item_id AS VARCHAR)),
    COUNT(*) - COUNT(DISTINCT order_id || '_' || CAST(order_item_id AS VARCHAR))
FROM raw_order_items
UNION ALL
SELECT 
    'products',
    'product_id',
    COUNT(*),
    COUNT(DISTINCT product_id),
    COUNT(*) - COUNT(DISTINCT product_id)
FROM raw_products
UNION ALL
SELECT 
    'customers',
    'customer_id',
    COUNT(*),
    COUNT(DISTINCT customer_id),
    COUNT(*) - COUNT(DISTINCT customer_id)
FROM raw_customers
UNION ALL
SELECT 
    'sellers_csv',
    'seller_id',
    COUNT(*),
    COUNT(DISTINCT seller_id),
    COUNT(*) - COUNT(DISTINCT seller_id)
FROM raw_sellers
UNION ALL
SELECT 
    'sellers_json',
    'seller_id',
    COUNT(*),
    COUNT(DISTINCT seller_id),
    COUNT(*) - COUNT(DISTINCT seller_id)
FROM raw_sellers_json
UNION ALL
SELECT 
    'reviews',
    'review_id',
    COUNT(*),
    COUNT(DISTINCT review_id),
    COUNT(*) - COUNT(DISTINCT review_id)
FROM raw_reviews;


-- ----------------------------------------------------------------------------
-- 4. Deep Inspection of JSON Seller Profiles (Concrete Findings)
-- ----------------------------------------------------------------------------
SELECT '=== 3. JSON SELLER PROFILES DEEP INSPECTION ===' AS section;

-- Finding 1: Duplicate seller records and multiple updated_at timestamps
SELECT 
    seller_id,
    COUNT(*) AS records_count,
    MIN(updated_at) AS earliest_update,
    MAX(updated_at) AS latest_update
FROM raw_sellers_json
GROUP BY seller_id
HAVING COUNT(*) > 1
ORDER BY records_count DESC
LIMIT 10;

-- Finding 2: Inconsistent casing and whitespace in profile.tier
SELECT 
    profile.tier AS raw_tier,
    LOWER(TRIM(profile.tier)) AS cleaned_tier,
    COUNT(*) AS occurrence_count
FROM raw_sellers_json
GROUP BY profile.tier
ORDER BY raw_tier;

-- Finding 3: Missing shipping information (null handling days and carriers)
SELECT 
    COUNT(*) AS total_json_records,
    COUNT(CASE WHEN shipping IS NULL THEN 1 END) AS null_shipping_struct,
    COUNT(CASE WHEN shipping.handling_days IS NULL THEN 1 END) AS null_handling_days,
    COUNT(CASE WHEN shipping.carriers IS NULL THEN 1 END) AS null_carriers
FROM raw_sellers_json;


-- ----------------------------------------------------------------------------
-- 5. Cross-Dataset Referential Consistency (CSV vs JSON Sellers)
-- ----------------------------------------------------------------------------
SELECT '=== 4. CSV VS JSON SELLERS RECONCILIATION ===' AS section;

SELECT 
    (SELECT COUNT(DISTINCT seller_id) FROM raw_sellers) AS sellers_in_csv,
    (SELECT COUNT(DISTINCT seller_id) FROM raw_sellers_json) AS sellers_in_json,
    (SELECT COUNT(DISTINCT s.seller_id) 
     FROM raw_sellers s 
     LEFT JOIN raw_sellers_json j ON s.seller_id = j.seller_id 
     WHERE j.seller_id IS NULL) AS csv_sellers_missing_in_json,
    (SELECT COUNT(DISTINCT j.seller_id) 
     FROM raw_sellers_json j 
     LEFT JOIN raw_sellers s ON j.seller_id = s.seller_id 
     WHERE s.seller_id IS NULL) AS json_sellers_missing_in_csv;


-- ----------------------------------------------------------------------------
-- 6. Null Rate Analysis in Core Tables
-- ----------------------------------------------------------------------------
SELECT '=== 5. NULL RATE ANALYSIS IN ORDERS & PRODUCTS ===' AS section;

SELECT 
    'orders' AS table_name,
    COUNT(*) AS total_rows,
    COUNT(CASE WHEN order_approved_at IS NULL THEN 1 END) AS null_approved_at,
    ROUND(COUNT(CASE WHEN order_approved_at IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) AS pct_null_approved,
    COUNT(CASE WHEN order_delivered_carrier_date IS NULL THEN 1 END) AS null_carrier_date,
    ROUND(COUNT(CASE WHEN order_delivered_carrier_date IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) AS pct_null_carrier,
    COUNT(CASE WHEN order_delivered_customer_date IS NULL THEN 1 END) AS null_delivered_customer_date,
    ROUND(COUNT(CASE WHEN order_delivered_customer_date IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) AS pct_null_delivered
FROM raw_orders;

SELECT 
    'products' AS table_name,
    COUNT(*) AS total_rows,
    COUNT(CASE WHEN product_category_name IS NULL THEN 1 END) AS null_category_pt,
    ROUND(COUNT(CASE WHEN product_category_name IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) AS pct_null_category,
    COUNT(CASE WHEN product_weight_g IS NULL THEN 1 END) AS null_weight,
    COUNT(CASE WHEN product_length_cm IS NULL THEN 1 END) AS null_dimensions
FROM raw_products;


-- ----------------------------------------------------------------------------
-- 7. Referential Integrity Check of Order Items against Entities
-- ----------------------------------------------------------------------------
SELECT '=== 6. FOREIGN KEY INTEGRITY IN RAW ORDER ITEMS ===' AS section;

SELECT 
    'order_items -> orders' AS fk_relation,
    COUNT(*) AS missing_parent_keys
FROM raw_order_items oi
LEFT JOIN raw_orders o ON oi.order_id = o.order_id
WHERE o.order_id IS NULL
UNION ALL
SELECT 
    'order_items -> products',
    COUNT(*)
FROM raw_order_items oi
LEFT JOIN raw_products p ON oi.product_id = p.product_id
WHERE p.product_id IS NULL
UNION ALL
SELECT 
    'order_items -> sellers (csv)',
    COUNT(*)
FROM raw_order_items oi
LEFT JOIN raw_sellers s ON oi.seller_id = s.seller_id
WHERE s.seller_id IS NULL
UNION ALL
SELECT 
    'orders -> customers',
    COUNT(*)
FROM raw_orders o
LEFT JOIN raw_customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
