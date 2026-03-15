-- Clean product events: cast timestamps, deduplicate
with source as (
    select * from {{ source('raw', 'product_events') }}
),

cleaned as (
    select
        event_id,
        user_id,
        event_type,
        cast(event_timestamp as timestamp) as event_timestamp,
        cast(event_timestamp as date) as event_date,
        session_id,
        platform
    from source
    where user_id is not null
      and event_timestamp is not null
),

-- Remove exact duplicates (same event_id)
deduplicated as (
    select *,
        row_number() over (partition by event_id order by event_timestamp) as row_num
    from cleaned
)

select
    event_id,
    user_id,
    event_type,
    event_timestamp,
    event_date,
    session_id,
    platform
from deduplicated
where row_num = 1
