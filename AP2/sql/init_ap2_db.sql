-- ============================================================================
-- NorthMart Data Platform - AP2 Database Initialization
-- Engine: DuckDB
-- Description:
--   Resets the fact table built in AP1 so the AP2 ELT pipeline populates it
--   incrementally from the Mock REST API, and creates the raw landing table.
-- ============================================================================

-- 1. Empty the PA1/AP1 fact table while keeping dimensions intact
DELETE FROM fact_sales;

-- 2. Reset AP2 staging and raw landing tables
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

