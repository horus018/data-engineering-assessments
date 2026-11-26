-- NorthMart Data Platform - PA3 Part A Task 3: GDPR Right to Erasure (Art. 17)
-- Removes a customer across all DuckDB layers (marts, staging, raw tables)
-- and refreshes the curated Parquet exports (data/curated/).
--
-- Parameters injected or set via DuckDB session variables:
--   getvariable('target_customer_id')   : Raw customer_id requested for erasure
--   getvariable('target_hash_key')      : Secret NORTHMART_HASH_KEY from environment

BEGIN TRANSACTION;

-- 1. Identify all raw customer_ids belonging to the same person (via customer_unique_id)
CREATE OR REPLACE TEMP TABLE _erasure_targets AS
SELECT DISTINCT
    c2.customer_id AS raw_customer_id,
    c2.customer_unique_id AS raw_customer_unique_id,
    sha256(getvariable('target_hash_key') || TRIM(c2.customer_id)) AS customer_id_hash,
    sha256(getvariable('target_hash_key') || TRIM(c2.customer_unique_id)) AS customer_unique_id_hash
FROM raw_customers c1
JOIN raw_customers c2
  ON c1.customer_unique_id = c2.customer_unique_id
WHERE c1.customer_id = getvariable('target_customer_id')
   OR c1.customer_unique_id = getvariable('target_customer_id')

UNION

SELECT
    getvariable('target_customer_id') AS raw_customer_id,
    getvariable('target_customer_id') AS raw_customer_unique_id,
    sha256(getvariable('target_hash_key') || TRIM(getvariable('target_customer_id'))) AS customer_id_hash,
    sha256(getvariable('target_hash_key') || TRIM(getvariable('target_customer_id'))) AS customer_unique_id_hash;

-- 2. Identify target surrogate customer_keys in dim_customer
CREATE OR REPLACE TEMP TABLE _erasure_keys AS
SELECT DISTINCT customer_key
FROM dim_customer
WHERE customer_id IN (SELECT customer_id_hash FROM _erasure_targets)
   OR customer_unique_id IN (SELECT customer_unique_id_hash FROM _erasure_targets)
   OR customer_id IN (SELECT raw_customer_id FROM _erasure_targets);

-- 3. Delete from Marts (fact_sales and dim_customer)
DELETE FROM fact_sales
WHERE customer_key IN (SELECT customer_key FROM _erasure_keys);

DELETE FROM dim_customer
WHERE customer_key IN (SELECT customer_key FROM _erasure_keys)
   OR customer_id IN (SELECT customer_id_hash FROM _erasure_targets)
   OR customer_unique_id IN (SELECT customer_unique_id_hash FROM _erasure_targets);

-- 4. Delete from Staging (stg_orders)
DELETE FROM stg_orders
WHERE customer_id IN (SELECT customer_id_hash FROM _erasure_targets)
   OR customer_id IN (SELECT raw_customer_id FROM _erasure_targets);

-- 5. Delete from Raw Tables in DuckDB (raw_api_orders, raw_orders, raw_customers)
DELETE FROM raw_api_orders
WHERE customer_id IN (SELECT raw_customer_id FROM _erasure_targets);

DELETE FROM raw_orders
WHERE customer_id IN (SELECT raw_customer_id FROM _erasure_targets);

DELETE FROM raw_customers
WHERE customer_id IN (SELECT raw_customer_id FROM _erasure_targets)
   OR customer_unique_id IN (SELECT raw_customer_unique_id FROM _erasure_targets);

COMMIT;

-- 6. Re-export Curated Parquet Layouts (unpartitioned and partitioned) without the erased customer
COPY fact_sales TO 'data/curated/fact_sales.parquet'
(FORMAT PARQUET, COMPRESSION ZSTD, OVERWRITE TRUE);

COPY fact_sales TO 'data/curated/fact_sales_partitioned'
(FORMAT PARQUET, PARTITION_BY (year_month), COMPRESSION ZSTD, OVERWRITE TRUE);

