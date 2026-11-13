-- Custom business rule test (Task 3):
-- Validates order-level marketplace economics and batch-date alignment.
-- Every order in a daily settlement batch must have:
--   1. Positive net merchandise revenue (SUM(price) > 0)
--   2. Total settlement strictly greater than shipping fees (SUM(total_item_value) > SUM(freight_value))
--   3. Purchase date equal to the requested API batch_date

SELECT
    order_id,
    batch_date,
    MIN(CAST(order_purchase_timestamp AS DATE)) AS min_purchase_date,
    MAX(CAST(order_purchase_timestamp AS DATE)) AS max_purchase_date,
    SUM(price) AS order_merchandise_revenue,
    SUM(freight_value) AS order_freight_total,
    SUM(total_item_value) AS order_gross_settlement
FROM {{ ref('stg_orders') }}
GROUP BY order_id, batch_date
HAVING
    SUM(price) <= 0
    OR SUM(total_item_value) <= SUM(freight_value)
    OR MIN(CAST(order_purchase_timestamp AS DATE)) <> batch_date
    OR MAX(CAST(order_purchase_timestamp AS DATE)) <> batch_date

