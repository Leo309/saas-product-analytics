# KPI Definitions

## Feature Adoption Metrics

### Adoption Funnel
Tracks the AI Caption Generator adoption journey.

| Stage | Definition | Formula |
|-------|-----------|---------|
| **Exposed** | Users who saw the feature (banner, tooltip, email) | `COUNT(DISTINCT user_id) WHERE event_type = 'exposed'` |
| **First Use** | Users who tried the feature at least once | `COUNT(DISTINCT user_id) WHERE event_type = 'first_use'` |
| **Repeat User** | Users who used it more than once within 7 days | `COUNT(DISTINCT user_id) WHERE event_type = 'repeat_use'` |
| **Exposure → First Use Rate** | Conversion from seeing to trying | `first_use_users / exposed_users × 100` |
| **First Use → Repeat Rate** | Conversion from trying to repeating | `repeat_users / first_use_users × 100` |

### Time to Adopt
- **Definition**: Days from first exposure to first use
- **Formula**: `DATEDIFF(first_use_date, exposure_date)`
- **Why it matters**: Identifies UX friction — if users take >14 days, the feature isn't compelling enough at first glance
- **Benchmark**: <7 days is strong for a self-serve feature

---

## Retention Metrics

### Cohort Retention (Adopters vs Non-Adopters)
- **Definition**: % of users still active at 30/60/90 days, segmented by adoption status
- **Segments**:
  - Adopters (used AI Caption Generator)
  - Exposed non-adopters (saw it but didn't use)
  - Unexposed (never saw it)
- **Formula**: `active_users_at_day_N / cohort_size × 100`
- **Why it matters**: Proves (or disproves) that the feature drives retention — key for product team investment decisions

---

## Engagement Metrics

### DAU/MAU Ratio
- **Definition**: Daily active users / Monthly active users — measures stickiness
- **Formula**: `AVG(daily_active_users) / COUNT(DISTINCT monthly_active_users)`
- **Pre vs Post**: Compare Jan–May (before launch) vs Jul–Dec (after launch)
- **Benchmark**: >25% = strong engagement

### Sessions per User
- **Definition**: Average login sessions per user per month
- **Formula**: `COUNT(login_events) / COUNT(DISTINCT active_users)`
- **Segmented by**: Adopters vs non-adopters

---

## Subscription Metrics (Supporting)

### MRR by Plan
- **Definition**: Monthly recurring revenue by plan tier
- **Formula**: `SUM(mrr) WHERE status = 'active' GROUP BY plan`

### Churn Rate
- **Definition**: % of paying users who cancel per month
- **Formula**: `cancelled_users / beginning_of_month_users × 100`
- **Segmented by**: Adopters vs non-adopters (does the feature reduce churn?)
