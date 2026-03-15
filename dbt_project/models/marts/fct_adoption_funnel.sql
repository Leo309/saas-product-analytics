-- Feature adoption funnel: monthly breakdown by plan tier
-- Tracks: total users → exposed → first use → repeat use
with users as (
    select * from {{ ref('dim_users') }}
),

-- Monthly cohorts based on when users were first exposed
monthly_funnel as (
    select
        date_trunc(first_exposed_date, month) as exposure_month,
        current_plan,

        -- Funnel counts
        count(distinct user_id) as exposed_users,
        count(distinct case
            when adoption_segment in ('one_time_adopter', 'repeat_adopter')
            then user_id
        end) as first_use_users,
        count(distinct case
            when adoption_segment = 'repeat_adopter'
            then user_id
        end) as repeat_users,

        -- Time to adopt stats
        avg(days_to_adopt) as avg_days_to_adopt,
        approx_quantiles(days_to_adopt, 100)[offset(50)] as median_days_to_adopt

    from users
    where first_exposed_date is not null
    group by 1, 2
),

with_rates as (
    select
        exposure_month,
        current_plan,
        exposed_users,
        first_use_users,
        repeat_users,

        -- Conversion rates
        round(safe_divide(first_use_users, exposed_users) * 100, 1) as exposure_to_use_rate,
        round(safe_divide(repeat_users, first_use_users) * 100, 1) as use_to_repeat_rate,
        round(safe_divide(repeat_users, exposed_users) * 100, 1) as overall_adoption_rate,

        avg_days_to_adopt,
        median_days_to_adopt

    from monthly_funnel
)

select * from with_rates
order by exposure_month, current_plan
