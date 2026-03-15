-- Cohort retention: compare adopters vs non-adopters at 30/60/90 days
-- Key question: does using the AI Caption Generator improve retention?
with users as (
    select * from {{ ref('dim_users') }}
),

events as (
    select * from {{ ref('stg_events') }}
),

-- Define the cohort: users who signed up before feature launch
-- so we have a fair comparison window
cohort_users as (
    select
        user_id,
        signup_date,
        adoption_segment,
        current_plan
    from users
    where signup_date < '2025-06-01'  -- Pre-launch signups only
),

-- Check if user was active in each retention window (post-launch)
user_activity as (
    select
        cu.user_id,
        cu.signup_date,
        cu.adoption_segment,
        cu.current_plan,

        -- Was active within 30/60/90 days after feature launch (2025-06-01)
        max(case
            when e.event_date between '2025-06-01' and date_add('2025-06-01', interval 30 day)
            then 1 else 0
        end) as active_30d,
        max(case
            when e.event_date between '2025-06-01' and date_add('2025-06-01', interval 60 day)
            then 1 else 0
        end) as active_60d,
        max(case
            when e.event_date between '2025-06-01' and date_add('2025-06-01', interval 90 day)
            then 1 else 0
        end) as active_90d

    from cohort_users cu
    left join events e on cu.user_id = e.user_id
    group by 1, 2, 3, 4
),

-- Aggregate retention by adoption segment
retention_summary as (
    select
        adoption_segment,
        count(distinct user_id) as cohort_size,

        round(safe_divide(sum(active_30d), count(distinct user_id)) * 100, 1) as retention_30d,
        round(safe_divide(sum(active_60d), count(distinct user_id)) * 100, 1) as retention_60d,
        round(safe_divide(sum(active_90d), count(distinct user_id)) * 100, 1) as retention_90d

    from user_activity
    group by 1
)

select * from retention_summary
order by
    case adoption_segment
        when 'repeat_adopter' then 1
        when 'one_time_adopter' then 2
        when 'exposed_non_adopter' then 3
        when 'unexposed' then 4
    end
