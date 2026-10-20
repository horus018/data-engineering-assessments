# Data Engineering Practical Assessments (2026/2027)

**Institution**: Universidade Politécnica de Bragança (UPB)  
**Academic Year**: 2026/2027  
**Course**: Data Engineering  

---

## Repository Overview

This repository hosts the practical coursework platform developed across three sequential assessments (PA1, PA2, and PA3) as defined in the **Data Engineering — Practical Assessments Student Brief**:

```
project/
├── AP1/                        # Assessment 1: Storage formats & analytical modelling (ACTIVE)
│   ├── README.md               # Written answers, profiling, Kimball modelling, benchmarks & Lakehouse evaluation
│   ├── requirements.txt        # Pinned dependencies (DuckDB, Pandas, PyArrow, Matplotlib)
│   ├── .gitignore              # Ignores raw sources, DuckDB files, environment secrets
│   ├── architecture/           # Star schema diagram (PNG and Mermaid)
│   ├── data/
│   │   ├── source/             # Raw Kaggle Olist CSV files & seller JSON (gitignored)
│   │   └── curated/            # Exported Parquet files (unpartitioned & partitioned)
│   ├── sql/
│   │   ├── profiling.sql       # Task 1: Comprehensive DuckDB profiling
│   │   ├── build_model.sql     # Task 3: Star schema ETL with surrogate keys & referential checks
│   │   └── benchmark.sql       # Task 4: Analytical benchmark queries across layouts
│   ├── src/
│   │   ├── run_benchmark.py    # Automated timing harness across CSV and Parquet
│   │   └── generate_diagram.py # Star schema PNG diagram generator
│   ├── tests/
│   │   ├── test_referential_integrity.sql # SQL referential assertions
│   │   └── run_tests.py        # Automated test execution script
│   └── evidence/
│       ├── benchmark_results.md# Measured storage footprints & query latencies
│       ├── benchmark_table.csv # Benchmark metrics in CSV format
│       ├── profiling_output.txt# Profiling logs
│       └── referential_checks_output.txt # Integrity check logs
├── AP2/                        # Assessment 2: Orchestrated and tested ELT pipeline (Airflow + dbt)
├── AP3/                        # Assessment 3: Data protection & tool exploration (GDPR erasure + Spark/Kafka)
├── json_northmart_seller_profiles.json # Root copy of operational seller profiles
├── requirements.txt            # Global project requirements
└── .gitignore                  # Global repository gitignore
```

---

## Practical Assessment Status

| Assessment | Scope | Status | Weight | Submission | Defense |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **PA1 (AP1)** | **Storage Formats & Analytical Modelling (Star Schema, DuckDB, Parquet)** | **COMPLETED** | **20%** | **17/10/2026** | **19/10/2026** |
| **PA2 (AP2)** | Orchestrated & Tested ELT Pipeline (FastAPI mock, dbt, Airflow) | Upcoming | 20% | 14/11/2026 | 16/11/2026 |
| **PA3 (AP3)** | Data Protection (GDPR erasure, hashing) & Tool Exploration | Upcoming | 20% | 12/12/2026 | 14/12/2026 |

---

## Quick Start (PA1 / AP1)

To run the complete PA1 analytical workflow:

```bash
# 1. Navigate to AP1 directory
cd AP1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Profile raw CSV exports and JSON profiles
duckdb < sql/profiling.sql

# 4. Build Kimball star schema, verify referential integrity, and export to Parquet
duckdb northmart.duckdb < sql/build_model.sql

# 5. Execute benchmark suite across CSV and Parquet layouts
python3 src/run_benchmark.py

# 6. Run automated referential integrity assertions
python3 tests/run_tests.py
```

For complete documentation, analysis of findings, and architectural justifications, see:

- [AP1/README.md](AP1/README.md)
