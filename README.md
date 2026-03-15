# SaaS Feature Adoption Analytics

> Deep-dive analytics pipeline for a social media management tool (inspired by Hootsuite), analyzing the launch of an "AI Caption Generator" feature — from adoption funnel to retention impact. Built with BigQuery + dbt + Airflow + Looker Studio.

## Business Context

A simulated social media management platform (~2,000 users across Free, Pro, and Enterprise tiers). On **2025-06-01**, a new **AI Caption Generator** feature launches. This project answers:

- **Who adopted the feature?** — Adoption funnel: exposure → first use → repeat use
- **How fast?** — Time-to-adopt distribution after launch
- **Did it improve retention?** — Cohort retention: adopters vs non-adopters (30/60/90 days)
- **Did engagement change?** — DAU/MAU before vs after launch

## Architecture

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│    Users     │   │ Subscriptions│   │   Product    │   │   Feature    │
│     CSV      │   │     CSV      │   │  Events CSV  │   │ Exposures CSV│
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │                  │
       └──────────┬───────┴──────────┬───────┴──────────┬───────┘
                  ▼                  ▼                  ▼
        ┌────────────────────────────────────────────────────┐
        │            BigQuery (Raw Dataset)                  │
        │            CSV → raw tables                       │
        └────────────────────────┬───────────────────────────┘
                                 ▼
        ┌────────────────────────────────────────────────────┐
        │            dbt Staging Models                     │
        │            Clean, cast, deduplicate               │
        └────────────────────────┬───────────────────────────┘
                                 ▼
        ┌────────────────────────────────────────────────────┐
        │            dbt Mart Models                        │
        │            Adoption funnel, cohort retention,     │
        │            engagement metrics                     │
        └────────────────────────┬───────────────────────────┘
                                 ▼
        ┌────────────────────────────────────────────────────┐
        │            Airflow (Docker)                       │
        │            Scheduled DAG, dbt build + test        │
        └────────────────────────┬───────────────────────────┘
                                 ▼
        ┌────────────────────────────────────────────────────┐
        │            Looker Studio Dashboard                │
        │            Feature adoption & retention analysis  │
        └────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Data Generation | Python (Faker, Pandas) |
| Data Warehouse | Google BigQuery |
| Transformation | dbt-bigquery |
| Data Testing | dbt tests (not_null, unique, accepted_values, relationships) |
| Documentation | dbt docs (auto-generated data dictionary) |
| Orchestration | Apache Airflow (Docker Compose) |
| Visualization | Looker Studio |
| Version Control | Git + GitHub |

## Analysis Focus

### 1. Feature Adoption Funnel
Exposure → First Use → Repeat Use (7-day) → Power User (weekly active)

### 2. Cohort Retention
Compare 30/60/90-day retention rates between:
- Users who adopted AI Caption Generator
- Users who were exposed but did not adopt
- Users who were never exposed

### 3. Time to Adopt
Distribution of days from feature exposure to first use — identifies friction points.

### 4. Engagement Impact
DAU/MAU ratio before (Jan–May) vs after (Jun–Dec) feature launch, segmented by adoption status.

## Data Sources

| Source | Description | Rows |
|--------|------------|------|
| `users.csv` | User profiles, plan tier, signup date | ~2,000 |
| `subscriptions.csv` | Subscription lifecycle events | ~2,500 |
| `product_events.csv` | User activity logs (login, post, schedule, etc.) | ~200K |
| `feature_exposures.csv` | AI Caption Generator exposure + usage events | ~15K |

## Project Structure

```
saas-product-analytics/
├── README.md
├── data/
│   ├── raw/                        # Simulated raw data files
│   │   ├── users.csv
│   │   ├── subscriptions.csv
│   │   ├── product_events.csv
│   │   └── feature_exposures.csv
│   ├── generate_data.py            # Data generation script
│   └── requirements.txt
├── dbt_project/                    # dbt transformation layer
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── staging/                # Clean & cast raw data
│   │   │   ├── stg_users.sql
│   │   │   ├── stg_subscriptions.sql
│   │   │   ├── stg_events.sql
│   │   │   └── stg_feature_exposures.sql
│   │   └── marts/                  # Business metrics
│   │       ├── fct_adoption_funnel.sql
│   │       ├── fct_cohort_retention.sql
│   │       ├── fct_engagement_metrics.sql
│   │       └── dim_users.sql
│   ├── tests/                      # Custom data tests
│   └── macros/
├── airflow/                        # Airflow orchestration
│   ├── docker-compose.yml
│   └── dags/
│       └── feature_analytics_dag.py
├── reports/                        # Dashboard screenshots
└── docs/
    ├── architecture.md
    └── kpi_definitions.md
```

## Comparison with Microsoft Stack Project

| Dimension | [E-Commerce (Fabric)](https://github.com/Leo309/ecommerce-analytics) | SaaS Feature Adoption (Modern Stack) |
|-----------|------|------|
| Warehouse | Fabric Lakehouse (Delta) | BigQuery |
| Transformation | PySpark Notebooks | dbt (SQL) |
| Orchestration | Fabric Pipeline | Airflow (Docker) |
| Visualization | Power BI (DirectLake) | Looker Studio |
| Data Testing | Manual validation | dbt tests (automated) |
| Documentation | Manual markdown | dbt docs (auto-generated) |
| Analysis Depth | Broad (revenue, product, channel) | Deep (single feature launch analysis) |
| Business Domain | Multi-channel e-commerce | B2B SaaS product analytics |

## Getting Started

### Prerequisites
- Google Cloud account (free tier)
- Python 3.10+
- Docker Desktop
- dbt-bigquery (`pip install dbt-bigquery`)

### Generate Simulated Data
```bash
cd data
pip install -r requirements.txt
python generate_data.py
```

## License

MIT
