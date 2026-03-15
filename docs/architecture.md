# Architecture Overview

## Data Flow

```
Python (simulated CSV)
  → BigQuery Raw Dataset
    → dbt Staging (clean, cast, dedup)
      → dbt Marts (funnel, cohort, engagement)
        → Looker Studio Dashboard

Airflow DAG (Docker) orchestrates: load → staging → marts → tests
```

## Data Sources

### 1. Users (`users.csv`)
User profiles with plan tier, company info, signup date.
- ~2,000 rows, one per user
- Includes intentional quality issues (missing dates, uppercase emails)

### 2. Subscriptions (`subscriptions.csv`)
Subscription lifecycle events: created, upgraded, downgraded, cancelled.
- ~2,500 rows
- Tracks plan changes and MRR over time

### 3. Product Events (`product_events.csv`)
Core platform activity: login, post_create, post_schedule, analytics_view, etc.
- ~200K rows
- Full year (2025-01 to 2025-12)
- Used for DAU/MAU calculation

### 4. Feature Exposures (`feature_exposures.csv`)
AI Caption Generator-specific events: exposed, first_use, repeat_use.
- ~15K rows
- Only after 2025-06-01 (feature launch date)
- Includes exposure context (banner, tooltip, email, notification)

## dbt Layer Design

### Staging (`stg_*`)
- `stg_users` — Clean emails, cast dates, handle nulls
- `stg_subscriptions` — Cast dates, validate plan values
- `stg_events` — Deduplicate, cast timestamps
- `stg_feature_exposures` — Cast timestamps, validate event types

### Marts (`fct_*`, `dim_*`)
- `dim_users` — Enriched user dimension with adoption status
- `fct_adoption_funnel` — Funnel metrics: exposed → first use → repeat use
- `fct_cohort_retention` — Retention comparison: adopters vs non-adopters
- `fct_engagement_metrics` — DAU/MAU before vs after feature launch

## Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Analysis scope | Single feature deep-dive | Depth > breadth, tells a complete data story |
| Feature launch date | 2025-06-01 | Gives 5 months before + 7 months after for comparison |
| Funnel definition | exposed → first_use → repeat_use | Standard product adoption framework |
| Retention windows | 30/60/90 days | Industry-standard SaaS retention periods |
| Warehouse | BigQuery | Free tier (1TB query/mo), serverless, Looker-native |
| Orchestration | Airflow in Docker | Industry standard, most requested in DE job postings |
