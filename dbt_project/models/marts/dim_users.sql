-- Enriched user dimension with feature adoption status
-- Segments: adopter (used feature), exposed (saw but didn't use), unexposed
with users as (
    select * from {{ ref('stg_users') }}
),

-- Get each user's latest subscription status
latest_subscription as (
    select
        user_id,
        plan,
        mrr,
        event_type as subscription_status,
        event_date as last_subscription_date
    from (
        select *,
            row_number() over (partition by user_id order by event_date desc) as rn
        from {{ ref('stg_subscriptions') }}
    )
    where rn = 1
),

-- Determine feature adoption status per user
feature_status as (
    select
        user_id,
        min(case when event_type = 'exposed' then event_date end) as first_exposed_date,
        min(case when event_type = 'first_use' then event_date end) as first_use_date,
        min(case when event_type = 'repeat_use' then event_date end) as first_repeat_date,
        countif(event_type = 'repeat_use') as repeat_use_count
    from {{ ref('stg_feature_exposures') }}
    group by user_id
),

enriched as (
    select
        u.user_id,
        u.email,
        u.full_name,
        u.company_name,
        u.industry,
        u.company_size,
        u.country,
        coalesce(ls.plan, u.plan) as current_plan,
        coalesce(ls.mrr, 0) as current_mrr,
        coalesce(ls.subscription_status, 'created') as subscription_status,
        u.signup_date,

        -- Feature adoption fields
        fs.first_exposed_date,
        fs.first_use_date,
        fs.first_repeat_date,
        coalesce(fs.repeat_use_count, 0) as repeat_use_count,

        -- Adoption segment
        case
            when fs.first_repeat_date is not null then 'repeat_adopter'
            when fs.first_use_date is not null then 'one_time_adopter'
            when fs.first_exposed_date is not null then 'exposed_non_adopter'
            else 'unexposed'
        end as adoption_segment,

        -- Time to adopt (days from exposure to first use)
        date_diff(fs.first_use_date, fs.first_exposed_date, day) as days_to_adopt

    from users u
    left join latest_subscription ls on u.user_id = ls.user_id
    left join feature_status fs on u.user_id = fs.user_id
)

select * from enriched
