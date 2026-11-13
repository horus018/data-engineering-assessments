-- NorthMart Data Platform - AP2 Database Initialization
-- Resets fact_sales so the AP2 pipeline fills it incrementally from the API,
-- while keeping the AP1 dimensions intact.

DELETE FROM fact_sales;

DROP TABLE IF EXISTS stg_orders;
DROP TABLE IF EXISTS raw_api_orders;

CREATE TABLE raw_api_orders (
    batch_date DATE NOT NULL,
    page INTEGER NOT NULL,
    order_id VARCHAR,
    order_item_id INTEGER,
    customer_id VARCHAR,
    product_id VARCHAR,
    seller_id VARCHAR,
    order_status VARCHAR,
    order_purchase_timestamp VARCHAR,
    price DOUBLE,
    freight_value DOUBLE,
    ingested_at TIMESTAMP NOT NULL
);
