-- One row per company from the newest SEC load.

with latest_snapshot as (
    select *
    from {{ source('sec', 'sec_company_profiles_flat') }}
    where ingest_date = (
        select max(ingest_date)
        from {{ source('sec', 'sec_company_profiles_flat') }}
    )
)

select
    ticker,
    cik,
    entity_name,
    entity_type,
    try_cast(sic as integer)    as sic_code,
    sic_description,
    fiscal_year_end             as latest_fiscal_year_end_mmdd,
    state_of_incorporation,
    listed_tickers,
    listed_exchanges,
    cast(ingest_date as date)   as ingest_date
from latest_snapshot