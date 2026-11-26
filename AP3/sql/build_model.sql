-- NorthMart Data Platform - AP3 Dimensional & Raw Foundation
-- Engine: DuckDB
-- Materializes raw tables in DuckDB so GDPR erasure (erase_customer.sql) can delete
-- records from the database raw layer while keeping data/source/ files untouched.

-- 1. Create Raw Tables & Views in DuckDB
CREATE OR REPLACE TABLE raw_orders AS 
SELECT * FROM read_csv_auto('data/source/olist_orders_dataset.csv');

CREATE OR REPLACE TABLE raw_order_items AS 
SELECT * FROM read_csv_auto('data/source/olist_order_items_dataset.csv');

CREATE OR REPLACE VIEW raw_products AS 
SELECT * FROM read_csv_auto('data/source/olist_products_dataset.csv');

CREATE OR REPLACE TABLE raw_customers AS 
SELECT * FROM read_csv_auto('data/source/olist_customers_dataset.csv');

CREATE OR REPLACE VIEW raw_sellers AS 
SELECT * FROM read_csv_auto('data/source/olist_sellers_dataset.csv');

CREATE OR REPLACE VIEW raw_category_translation AS 
SELECT * FROM read_csv_auto('data/source/product_category_name_translation.csv');

CREATE OR REPLACE VIEW raw_sellers_json AS 
SELECT * FROM read_json_auto('data/source/northmart_seller_profiles.json');

CREATE OR REPLACE TABLE raw_order_reviews AS 
SELECT * FROM read_csv_auto('data/source/olist_order_reviews_dataset.csv');


-- 2. Build Dimension Tables

-- 2.1 Date Dimension (dim_date)
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


-- 2.3 Customer Dimension Placeholder (replaced by dbt dim_customer with keyed SHA-256 hash)
CREATE OR REPLACE TABLE dim_customer AS
SELECT
    ROW_NUMBER() OVER (ORDER BY c.customer_id) AS customer_key,
    c.customer_id,
    c.customer_unique_id,
    SUBSTR(LPAD(TRIM(CAST(c.customer_zip_code_prefix AS VARCHAR)), 5, '0'), 1, 2) || 'XXX' AS zip_code_prefix,
    'REDACTED' AS city,
    COALESCE(UPPER(TRIM(c.customer_state)), 'UNKNOWN') AS state
FROM raw_customers c;


-- 2.4 Seller Dimension (dim_seller)
-- Note (GDPR Data Minimization): contact.email and contact.phone from raw_sellers_json are excluded
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


-- 3. Build Fact Table (fact_sales)
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

