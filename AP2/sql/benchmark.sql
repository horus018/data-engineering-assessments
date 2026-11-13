-- ============================================================================
-- NorthMart Data Platform - PA1 Task 4: Benchmark Queries
-- Engine: DuckDB
-- Description: Executes the three required analytical queries across 3 storage layouts:
--   1. Raw CSV Layout (Direct scan & on-the-fly joins over CSV exports)
--   2. Curated Parquet Unpartitioned (fact_sales.parquet + dimensions)
--   3. Curated Parquet Partitioned (fact_sales_partitioned by year_month + dimensions)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- LAYOUT 1: RAW CSV QUERIES
-- ----------------------------------------------------------------------------

-- Q1 (CSV): Revenue per month over the whole period
SELECT 
    strftime(o.order_purchase_timestamp, '%Y-%m') AS year_month,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    COUNT(*) AS total_items
FROM read_csv_auto('data/source/olist_order_items_dataset.csv') oi
JOIN read_csv_auto('data/source/olist_orders_dataset.csv') o ON oi.order_id = o.order_id
GROUP BY year_month
ORDER BY year_month;

-- Q2 (CSV): Revenue and item count for one single month (2018-05)
SELECT 
    strftime(o.order_purchase_timestamp, '%Y-%m') AS year_month,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    COUNT(*) AS total_items
FROM read_csv_auto('data/source/olist_order_items_dataset.csv') oi
JOIN read_csv_auto('data/source/olist_orders_dataset.csv') o ON oi.order_id = o.order_id
WHERE strftime(o.order_purchase_timestamp, '%Y-%m') = '2018-05'
GROUP BY year_month;

-- Q3 (CSV): The five product categories with the highest revenue
SELECT 
    COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category_name,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    COUNT(*) AS total_items
FROM read_csv_auto('data/source/olist_order_items_dataset.csv') oi
JOIN read_csv_auto('data/source/olist_products_dataset.csv') p ON oi.product_id = p.product_id
LEFT JOIN read_csv_auto('data/source/product_category_name_translation.csv') t ON p.product_category_name = t.product_category_name
GROUP BY category_name
ORDER BY total_revenue DESC
LIMIT 5;


-- ----------------------------------------------------------------------------
-- LAYOUT 2: UNPARTITIONED PARQUET QUERIES
-- ----------------------------------------------------------------------------

-- Q1 (Parquet Unpartitioned): Revenue per month over the whole period
SELECT 
    d.year_month,
    ROUND(SUM(f.price), 2) AS total_revenue,
    SUM(f.quantity) AS total_items
FROM read_parquet('data/curated/fact_sales.parquet') f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year_month
ORDER BY d.year_month;

-- Q2 (Parquet Unpartitioned): Revenue and item count for one single month (2018-05)
SELECT 
    d.year_month,
    ROUND(SUM(f.price), 2) AS total_revenue,
    SUM(f.quantity) AS total_items
FROM read_parquet('data/curated/fact_sales.parquet') f
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.year_month = '2018-05'
GROUP BY d.year_month;

-- Q3 (Parquet Unpartitioned): The five product categories with the highest revenue
SELECT 
    p.category_name,
    ROUND(SUM(f.price), 2) AS total_revenue,
    SUM(f.quantity) AS total_items
FROM read_parquet('data/curated/fact_sales.parquet') f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category_name
ORDER BY total_revenue DESC
LIMIT 5;


-- ----------------------------------------------------------------------------
-- LAYOUT 3: PARTITIONED PARQUET QUERIES (Partitioned by year_month)
-- ----------------------------------------------------------------------------

-- Q1 (Parquet Partitioned): Revenue per month over the whole period
SELECT 
    d.year_month,
    ROUND(SUM(f.price), 2) AS total_revenue,
    SUM(f.quantity) AS total_items
FROM read_parquet('data/curated/fact_sales_partitioned/**/*.parquet') f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year_month
ORDER BY d.year_month;

-- Q2 (Parquet Partitioned): Revenue and item count for one single month (2018-05)
-- Benefits from partition pruning: reads ONLY the 2018-05 partition folder!
SELECT 
    f.year_month,
    ROUND(SUM(f.price), 2) AS total_revenue,
    SUM(f.quantity) AS total_items
FROM read_parquet('data/curated/fact_sales_partitioned/**/*.parquet') f
WHERE f.year_month = '2018-05'
GROUP BY f.year_month;

-- Q3 (Parquet Partitioned): The five product categories with the highest revenue
SELECT 
    p.category_name,
    ROUND(SUM(f.price), 2) AS total_revenue,
    SUM(f.quantity) AS total_items
FROM read_parquet('data/curated/fact_sales_partitioned/**/*.parquet') f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category_name
ORDER BY total_revenue DESC
LIMIT 5;
