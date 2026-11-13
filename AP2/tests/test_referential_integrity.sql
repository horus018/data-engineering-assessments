-- Independent SQL checks run outside dbt on AP2/northmart.duckdb

-- 1. Date dimension foreign key
SELECT
    'test_fk_fact_sales_dim_date' AS test_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_sales f
LEFT JOIN dim_date d ON f.date_key = d.date_key
WHERE d.date_key IS NULL;

-- 2. Product dimension foreign key
SELECT
    'test_fk_fact_sales_dim_product' AS test_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_sales f
LEFT JOIN dim_product p ON f.product_key = p.product_key
WHERE p.product_key IS NULL;

-- 3. Customer dimension foreign key
SELECT
    'test_fk_fact_sales_dim_customer' AS test_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_sales f
LEFT JOIN dim_customer c ON f.customer_key = c.customer_key
WHERE c.customer_key IS NULL;

-- 4. Seller dimension foreign key
SELECT
    'test_fk_fact_sales_dim_seller' AS test_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_sales f
LEFT JOIN dim_seller s ON f.seller_key = s.seller_key
WHERE s.seller_key IS NULL;

-- 5. Positive price and non-negative freight
SELECT
    'test_measure_positive_price_non_neg_freight' AS test_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_sales
WHERE price <= 0 OR freight_value < 0 OR total_item_value <= 0;

-- 6. Grain uniqueness (order_id, order_item_id)
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

-- 7. Corrupted day (2018-05-09) blocked from fact_sales
SELECT
    'test_corrupted_day_20180509_blocked_from_marts' AS test_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM fact_sales
WHERE date_key = 20180509;
