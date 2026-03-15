-- Clean user profiles: lowercase emails, cast dates, handle nulls
with source as (
    select * from {{ source('raw', 'users') }}
),

cleaned as (
    select
        user_id,
        lower(email) as email,
        full_name,
        company_name,
        industry,
        company_size,
        country,
        plan,
        cast(signup_date as date) as signup_date
    from source
    where user_id is not null
      and signup_date is not null
)

select * from cleaned
