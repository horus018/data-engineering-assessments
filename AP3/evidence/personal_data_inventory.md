# PA3 Part A — Task 1: Personal Data Inventory (GDPR Classification)

Every field of the raw orders (`olist_orders_dataset.csv` and `raw_api_orders`), raw customers (`olist_customers_dataset.csv`), raw seller profiles (`northmart_seller_profiles.json` and `olist_sellers_dataset.csv`), and raw order reviews (`olist_order_reviews_dataset.csv`) is classified below as:
- **`identifier`** — Direct identifier that singles out an individual or legal person on its own (e.g., customer ID, email, phone).
- **`quasi-identifier`** — Indirect attribute that does not identify a person alone, but can re-identify an individual when combined with other attributes (e.g., 5-digit zip code prefix, city, exact timestamp, or free-text comment).
- **`non-personal`** — Technical, product, or financial metric that does not identify a natural person once detached from identifiers.

---

## 1. Raw Customers (`raw_customers` / `olist_customers_dataset.csv`)

| Field | Classification | Action in Marts (`dim_customer`) | Analytical Purpose | Retention Period |
|---|---|---|---|---|
| `customer_id` | `identifier` | **Keyed Hash** (`sha256(NORTHMART_HASH_KEY \|\| customer_id)`) | Join orders in `stg_orders` to `dim_customer` without exposing raw ID | **5 years** (statutory tax/accounting) or **immediate upon GDPR Art. 17 erasure** |
| `customer_unique_id` | `identifier` | **Keyed Hash** (`sha256(NORTHMART_HASH_KEY \|\| customer_unique_id)`) | Repeat-purchase & customer cohort retention analysis | **5 years** or **immediate upon GDPR Art. 17 erasure** |
| `customer_zip_code_prefix` | `quasi-identifier` | **Generalize** (`'75650'` $\rightarrow$ `'75XXX'`, 2-digit postal region) | Macro-regional logistics & freight zone analysis | **5 years** (in generalized form); erased upon GDPR request |
| `customer_city` | `quasi-identifier` | **Drop / Redact** (`'REDACTED'`) | Not needed in marts (small cities allow re-identification when combined with timestamps) | **30 days** in raw landing only; **0 days** in marts |
| `customer_state` | `quasi-identifier` | **Keep Generalized** (2-letter state code, e.g., `'SP'`, `'GO'`) | State-level revenue and regional sales reporting | **5 years**; erased upon GDPR request |

---

## 2. Raw Orders & API Feed (`raw_orders`, `raw_order_items`, `raw_api_orders`)

| Field | Classification | Action in Marts (`stg_orders` / `fact_sales`) | Analytical Purpose | Retention Period |
|---|---|---|---|---|
| `order_id` | `quasi-identifier` | **Keep** (order transaction key; dissociated from raw customer ID) | Composite fact grain `(order_id, order_item_id)` & idempotent `delete+insert` | **5 years** (tax audit trail); erased if linked customer requests GDPR erasure |
| `order_item_id` | `non-personal` | **Keep** | Line item sequence number (`1, 2, 3...`) within an order | **5 years** |
| `customer_id` | `identifier` | **Keyed Hash** in `stg_orders`; replaced by surrogate `customer_key` in `fact_sales` | Resolve foreign key `customer_key` in `fact_sales` | **30 days** in raw API table; hashed in staging; erased upon GDPR request |
| `product_id` | `non-personal` | **Keep** in staging; replaced by `product_key` in `fact_sales` | Product & category sales performance | **Indefinite** (non-personal catalog data) |
| `seller_id` | `identifier` (merchant ID) | **Keep** in staging; replaced by `seller_key` in `fact_sales` | Merchant revenue attribution & SLA tracking | **5 years** after seller contract termination |
| `order_status` | `non-personal` | **Keep** (normalized lowercase) | Order lifecycle & cancellation filtering | **5 years** |
| `order_purchase_timestamp` | `quasi-identifier` | **Generalize in Marts** to `date_key` (`YYYYMMDD`) & `year_month` (`YYYY-MM`) | Daily and monthly sales trend aggregation | **30 days** at second-precision in staging; **5 years** as daily `date_key` in marts |
| `order_approved_at` | `quasi-identifier` | **Drop** (not loaded into `fact_sales`) | Not required for sales revenue star schema | **30 days** in raw layer only |
| `order_delivered_carrier_date` | `quasi-identifier` | **Drop** (not loaded into `fact_sales`) | Not required for sales revenue star schema | **30 days** in raw layer only |
| `order_delivered_customer_date` | `quasi-identifier` | **Drop** (not loaded into `fact_sales`) | Not required for sales revenue star schema | **30 days** in raw layer only |
| `order_estimated_delivery_date` | `non-personal` | **Drop** (not loaded into `fact_sales`) | Not required for sales revenue star schema | **30 days** in raw layer only |
| `price` | `non-personal` | **Keep** (`DOUBLE`, rounded 2 decimals) | Gross merchandise revenue measure | **5 years** |
| `freight_value` | `non-personal` | **Keep** (`DOUBLE`, rounded 2 decimals) | Shipping cost measure | **5 years** |
| `batch_date` / `page` / `ingested_at` | `non-personal` | **Keep in Raw/Staging only** | Pipeline auditability & idempotent batch replacement | **30 days** operational retention |

---

## 3. Raw Seller Profiles (`raw_sellers_json` / `northmart_seller_profiles.json` & `raw_sellers`)

| Field | Classification | Action in Marts (`dim_seller`) | Analytical Purpose | Retention Period |
|---|---|---|---|---|
| `seller_id` | `identifier` | **Keep** (B2B merchant contractual identifier + surrogate `seller_key`) | Join sales items to seller dimension | **5 years** after seller contract ends |
| `contact.email` | `identifier` | **Drop** (excluded from `dim_seller`) | Direct contact PII — zero analytical purpose in BI marts | **0 days in marts** (kept only in operational CRM while contract is active) |
| `contact.phone` | `identifier` | **Drop** (excluded from `dim_seller`) | Direct contact PII — zero analytical purpose in BI marts | **0 days in marts** (kept only in operational CRM while contract is active) |
| `seller_zip_code_prefix` | `quasi-identifier` | **Keep** (commercial warehouse postal prefix) | Origin-to-destination freight route analysis | **5 years** |
| `seller_city` | `quasi-identifier` | **Keep** (commercial warehouse city) | Seller geographic distribution | **5 years** |
| `seller_state` | `quasi-identifier` | **Keep** (2-letter state code) | State-level merchant supply analysis | **5 years** |
| `profile.tier` | `non-personal` | **Keep** (normalized lowercase: `gold`, `silver`, `bronze`) | Revenue breakdown by seller tier | **5 years** |
| `profile.joined_on` | `quasi-identifier` | **Keep** (`DATE`) | Seller tenure & cohort analysis | **5 years** |
| `shipping.handling_days` | `non-personal` | **Keep** (`INTEGER`) | Warehouse dispatch efficiency metric | **5 years** |
| `shipping.carriers` | `non-personal` | **Drop** (nested array omitted from star schema) | Not required for order-item revenue analytics | **30 days** in raw layer |
| `updated_at` | `non-personal` | **Used in Staging only** (`QUALIFY ROW_NUMBER() ... ORDER BY updated_at DESC = 1`) | Deduplicate multiple JSON profile snapshots per seller | **30 days** in raw layer |

---

## 4. Raw Order Reviews (`raw_order_reviews` / `olist_order_reviews_dataset.csv`)

| Field | Classification | Action in Marts (`stg_reviews`) | Analytical Purpose | Retention Period |
|---|---|---|---|---|
| `review_id` | `non-personal` | **Keep** (in `stg_reviews`) | Primary key of structured review score | **2 years** |
| `order_id` | `quasi-identifier` | **Keep** (in `stg_reviews`) | Link satisfaction score to order | **2 years** (or erased upon customer GDPR request) |
| `review_score` | `non-personal` | **Keep** (`1` to `5` integer rating) | Customer satisfaction KPI aggregation | **5 years** |
| `review_comment_title` | `quasi-identifier` (High-risk Free Text) | **DROP — Never loaded into staging or marts** | Excluded: free text may contain customer names, phone numbers, addresses, or CPF | **0 days in analytical layer** |
| `review_comment_message` | `quasi-identifier` (High-risk Free Text) | **DROP — Never loaded into staging or marts** | Excluded: unstructured text cannot be safely anonymized via hashing | **0 days in analytical layer** |
| `review_creation_date` | `quasi-identifier` | **Keep** (`TIMESTAMP`) | Satisfaction trend over time | **2 years** |
| `review_answer_timestamp` | `non-personal` | **Keep** (`TIMESTAMP`) | Customer support response time SLA | **2 years** |

