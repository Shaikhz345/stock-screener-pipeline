-- One clean row per ticker per trading day, combining the daily

with daily as (
    select *, 'daily' as load_type
    from {{ source('tiingo', 'tiingo_daily_prices') }}
),

backfill as (
    select *, 'backfill' as load_type
    from {{ source('tiingo', 'tiingo_daily_prices_backfill') }}
),

unioned as (
    select * from daily
    union all
    select * from backfill
),

ranked as (
    select
        *,
        row_number() over (
            partition by ticker, substr("date", 1, 10)
            order by ingest_date desc, load_type desc
        ) as row_rank
    from unioned
)

select
    ticker,
    cast(substr("date", 1, 10) as date) as price_date,
    open                                as open_price,
    high                                as high_price,
    low                                 as low_price,
    close                               as close_price,
    cast(volume as bigint)              as volume,
    divcash                             as dividend_cash,
    splitfactor                         as split_factor,
    adjclose                            as vendor_adj_close,
    cast(ingest_date as date)           as ingest_date,
    load_type
from ranked
where row_rank = 1