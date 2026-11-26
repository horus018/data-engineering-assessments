{% set batch_date = var('batch_date', none) %}

SELECT
    CAST(batch_date AS DATE) AS batch_date,
    TRIM(order_id) AS order_id,
    CAST(order_item_id AS INTEGER) AS order_item_id,
    CASE
        WHEN order_id IS NOT NULL AND order_item_id IS NOT NULL
        THEN TRIM(order_id) || '-' || CAST(order_item_id AS VARCHAR)
        ELSE NULL
    END AS order_item_key,
    -- PA3 Task 2: Keyed SHA-256 hash for customer_id using secret key from env var.
    -- Preserves NULL when customer_id is missing so the not_null quality gate still fails on bad rows.
    CASE
        WHEN NULLIF(TRIM(customer_id), '') IS NOT NULL
        THEN sha256('{{ env_var("NORTHMART_HASH_KEY") }}' || TRIM(customer_id))
        ELSE NULL
    END AS customer_id,
    NULLIF(TRIM(product_id), '') AS product_id,
    NULLIF(TRIM(seller_id), '') AS seller_id,
    LOWER(TRIM(order_status)) AS order_status,
    CAST(order_purchase_timestamp AS TIMESTAMP) AS order_purchase_timestamp,
    CAST(strftime(CAST(order_purchase_timestamp AS TIMESTAMP), '%Y%m%d') AS INTEGER) AS date_key,
    strftime(CAST(order_purchase_timestamp AS TIMESTAMP), '%Y-%m') AS year_month,
    ROUND(CAST(price AS DOUBLE), 2) AS price,
    ROUND(CAST(freight_value AS DOUBLE), 2) AS freight_value,
    ROUND(CAST(price AS DOUBLE) + CAST(freight_value AS DOUBLE), 2) AS total_item_value,
    1 AS quantity,
    ingested_at
FROM {{ source('northmart_raw', 'raw_api_orders') }}
WHERE batch_date = {% if batch_date %}
    CAST('{{ batch_date }}' AS DATE)
{% else %}
    (
        SELECT batch_date
        FROM {{ source('northmart_raw', 'raw_api_orders') }}
        ORDER BY ingested_at DESC
        LIMIT 1
    )
{% endif %}

