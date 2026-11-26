{{ config(materialized='table') }}

-- PA3 Task 2 (GDPR Data Minimization):
-- Free-text fields (review_comment_title, review_comment_message) are explicitly omitted
-- so unstructured customer comments (which can contain names, phone numbers, addresses, CPFs)
-- are never loaded into staging or marts.
SELECT
    TRIM(review_id) AS review_id,
    TRIM(order_id) AS order_id,
    CAST(review_score AS INTEGER) AS review_score,
    CAST(review_creation_date AS TIMESTAMP) AS review_creation_date,
    CAST(review_answer_timestamp AS TIMESTAMP) AS review_answer_timestamp
FROM {{ source('northmart_raw', 'raw_order_reviews') }}
WHERE NULLIF(TRIM(review_id), '') IS NOT NULL
  AND NULLIF(TRIM(order_id), '') IS NOT NULL

