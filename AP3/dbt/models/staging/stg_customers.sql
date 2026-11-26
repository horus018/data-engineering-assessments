{{ config(materialized='table') }}

-- PA3 Task 2: Keyed SHA-256 hash on customer identifiers (key from env var NORTHMART_HASH_KEY)
-- and location generalization (5-digit zip -> 2-digit region 'NNXXX', city -> 'REDACTED', keep state).
SELECT
    sha256('{{ env_var("NORTHMART_HASH_KEY") }}' || TRIM(customer_id)) AS customer_id,
    sha256('{{ env_var("NORTHMART_HASH_KEY") }}' || TRIM(customer_unique_id)) AS customer_unique_id,
    SUBSTR(LPAD(TRIM(CAST(customer_zip_code_prefix AS VARCHAR)), 5, '0'), 1, 2) || 'XXX' AS zip_code_prefix,
    'REDACTED' AS city,
    COALESCE(UPPER(TRIM(customer_state)), 'UNKNOWN') AS state
FROM {{ source('northmart_raw', 'raw_customers') }}
WHERE NULLIF(TRIM(customer_id), '') IS NOT NULL

