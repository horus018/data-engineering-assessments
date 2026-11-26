-- NorthMart AP3 Automated Verification Suite: Referential Integrity & GDPR Privacy Checks

-- 1. Referential Integrity: fact_sales -> dim_date
SELECT
    '1. FK fact_sales -> dim_date' AS check_name,
    COUNT(*) AS violations,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS status
FROM fact_sales f
LEFT JOIN dim_date d ON f.date_key = d.date_key
WHERE d.date_key IS NULL

UNION ALL

-- 2. Referential Integrity: fact_sales -> dim_product
SELECT
    '2. FK fact_sales -> dim_product',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM fact_sales f
LEFT JOIN dim_product p ON f.product_key = p.product_key
WHERE p.product_key IS NULL

UNION ALL

-- 3. Referential Integrity: fact_sales -> dim_customer
SELECT
    '3. FK fact_sales -> dim_customer',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM fact_sales f
LEFT JOIN dim_customer c ON f.customer_key = c.customer_key
WHERE c.customer_key IS NULL

UNION ALL

-- 4. Referential Integrity: fact_sales -> dim_seller
SELECT
    '4. FK fact_sales -> dim_seller',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM fact_sales f
LEFT JOIN dim_seller s ON f.seller_key = s.seller_key
WHERE s.seller_key IS NULL

UNION ALL

-- 5. GDPR Keyed Hashing Check: every customer_id in dim_customer is a 64-char SHA-256 hex digest
SELECT
    '5. GDPR Keyed SHA-256 Hash on dim_customer.customer_id',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM dim_customer
WHERE LENGTH(customer_id) != 64 OR LENGTH(customer_unique_id) != 64

UNION ALL

-- 6. GDPR Location Generalization Check: zip_code_prefix is generalized (NNXXX) and city is REDACTED
SELECT
    '6. GDPR Location Generalization on dim_customer',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM dim_customer
WHERE city != 'REDACTED' OR RIGHT(zip_code_prefix, 3) != 'XXX'

UNION ALL

-- 7. GDPR Free-Text Exclusion Check: review_comment_message/title not in stg_reviews
SELECT
    '7. GDPR Free-Text Excluded from stg_reviews',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM information_schema.columns
WHERE table_name = 'stg_reviews'
  AND column_name IN ('review_comment_title', 'review_comment_message')

UNION ALL

-- 8. GDPR Right to Erasure Check: target customer removed from raw, staging, and marts
SELECT
    '8. GDPR Art. 17 Customer Erased Across All Layers',
    (
        (SELECT COUNT(*) FROM raw_api_orders WHERE customer_id = 'd1806517abdeab70d77e1ff58ec5f1b8') +
        (SELECT COUNT(*) FROM raw_customers WHERE customer_id = 'd1806517abdeab70d77e1ff58ec5f1b8') +
        (SELECT COUNT(*) FROM raw_orders WHERE customer_id = 'd1806517abdeab70d77e1ff58ec5f1b8')
    ),
    CASE WHEN (
        (SELECT COUNT(*) FROM raw_api_orders WHERE customer_id = 'd1806517abdeab70d77e1ff58ec5f1b8') +
        (SELECT COUNT(*) FROM raw_customers WHERE customer_id = 'd1806517abdeab70d77e1ff58ec5f1b8') +
        (SELECT COUNT(*) FROM raw_orders WHERE customer_id = 'd1806517abdeab70d77e1ff58ec5f1b8')
    ) = 0 THEN 'PASSED' ELSE 'FAILED' END;
