{{ config(materialized='table') }}

-- PA3 Task 2: Protected Customer Dimension (dim_customer)
-- Stores only keyed SHA-256 hashes of customer_id and customer_unique_id
-- and generalized location (2-digit zip region + state; exact city redacted).
SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id) AS customer_key,
    customer_id,
    customer_unique_id,
    zip_code_prefix,
    city,
    state
FROM {{ ref('stg_customers') }}

