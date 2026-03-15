-- Clean feature exposure events: cast timestamps, validate event types
with source as (
    select * from {{ source('raw', 'feature_exposures') }}
),

cleaned as (
    select
        exposure_id,
        user_id,
        event_type,
        cast(event_timestamp as timestamp) as event_timestamp,
        cast(event_timestamp as date) as event_date,
        feature_name,
        context
    from source
    where user_id is not null
      and event_type in ('exposed', 'first_use', 'repeat_use')
      and feature_name = 'ai_caption_generator'
)

select * from cleaned
