-- Clean subscription events: cast dates, validate plan values
with source as (
    select * from {{ source('raw', 'subscriptions') }}
),

cleaned as (
    select
        subscription_id,
        user_id,
        event_type,
        plan,
        cast(mrr as numeric) as mrr,
        cast(event_date as date) as event_date
    from source
    where user_id is not null
      and event_type in ('created', 'upgraded', 'downgraded', 'cancelled')
)

select * from cleaned
