-- Engagement metrics: DAU/MAU before vs after feature launch
-- Compares Jan-May (pre-launch) vs Jul-Dec (post-launch)
with events as (
    select * from {{ ref('stg_events') }}
),

users as (
    select user_id, adoption_segment
    from {{ ref('dim_users') }}
),

-- Daily active users by month and adoption segment
daily_active as (
    select
        {{ dbt_utils.date_trunc('month', 'e.event_date') }} as activity_month,
        e.event_date,
        u.adoption_segment,
        count(distinct e.user_id) as dau
    from events e
    join users u on e.user_id = u.user_id
    group by 1, 2, 3
),

-- Monthly active users
monthly_active as (
    select
        {{ dbt_utils.date_trunc('month', 'e.event_date') }} as activity_month,
        u.adoption_segment,
        count(distinct e.user_id) as mau
    from events e
    join users u on e.user_id = u.user_id
    group by 1, 2
),

-- Average DAU per month
avg_dau as (
    select
        activity_month,
        adoption_segment,
        round(avg(dau), 0) as avg_daily_active_users
    from daily_active
    group by 1, 2
),

-- Combine DAU/MAU
engagement as (
    select
        d.activity_month,
        d.adoption_segment,
        d.avg_daily_active_users,
        m.mau as monthly_active_users,
        round(safe_divide(d.avg_daily_active_users, m.mau) * 100, 1) as dau_mau_ratio,

        -- Pre vs post launch flag
        case
            when d.activity_month < '2025-06-01' then 'pre_launch'
            when d.activity_month >= '2025-07-01' then 'post_launch'
            else 'launch_month'
        end as period

    from avg_dau d
    join monthly_active m
        on d.activity_month = m.activity_month
        and d.adoption_segment = m.adoption_segment
)

select * from engagement
order by activity_month, adoption_segment
