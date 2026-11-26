{{
  config(
    materialized='incremental',
    unique_key=['order_id', 'order_item_id'],
    incremental_strategy='delete+insert'
  )
}}

SELECT
    s.date_key,
    s.year_month,
    p.product_key,
    c.customer_key,
    sl.seller_key,
    s.order_id,
    s.order_item_id,
    s.order_status,
    s.price,
    s.freight_value,
    s.total_item_value,
    s.quantity
FROM {{ ref('stg_orders') }} s
INNER JOIN {{ source('northmart_raw', 'dim_date') }} d
    ON s.date_key = d.date_key
INNER JOIN {{ source('northmart_raw', 'dim_product') }} p
    ON s.product_id = p.product_id
INNER JOIN {{ ref('dim_customer') }} c
    ON s.customer_id = c.customer_id
INNER JOIN {{ source('northmart_raw', 'dim_seller') }} sl
    ON s.seller_id = sl.seller_id

