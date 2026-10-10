-- ============================================================================
-- NorthMart Data Platform - Test Suite: Referential Integrity & Data Quality
-- Engine: DuckDB
-- Execution: duckdb northmart.duckdb < tests/test_referential_integrity.sql
-- ============================================================================

-- 1. Date Dimension Referential Integrity
SELECT 
    'test_fk_fact_sales_dim_date' AS test_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_sales f
LEFT JOIN dim_date d ON f.date_key = d.date_key
WHERE d.date_key IS NULL;

-- 2. Product Dimension Referential Integrity
SELECT 
    'test_fk_fact_sales_dim_product' AS test_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_sales f
LEFT JOIN dim_product p ON f.product_key = p.product_key
WHERE p.product_key IS NULL;

-- 3. Customer Dimension Referential Integrity
SELECT 
    'test_fk_fact_sales_dim_customer' AS test_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_sales f
LEFT JOIN dim_customer c ON f.customer_key = c.customer_key
WHERE c.customer_key IS NULL;

-- 4. Seller Dimension Referential Integrity
SELECT 
    'test_fk_fact_sales_dim_seller' AS test_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_sales f
LEFT JOIN dim_seller s ON f.seller_key = s.seller_key
WHERE s.seller_key IS NULL;

-- 5. Business Rule: Non-negative Sale Price and Freight
SELECT 
    'test_measure_non_negative_values' AS test_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_sales
WHERE price < 0 OR freight_value < 0 OR total_item_value < 0;

-- 6. Business Rule: Grain Uniqueness (order_id, order_item_id)
SELECT 
    'test_grain_uniqueness' AS test_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM (
    SELECT order_id, order_item_id, COUNT(*) AS cnt
    FROM fact_sales
    GROUP BY order_id, order_item_id
    HAVING COUNT(*) > 1
);
