-- One row per company, tag, unit, and reporting period, keeping the
-- most recently filed version. Each SEC load is a full snapshot,
-- so only the newest load is used.

with latest_snapshot as (
    select *
    from {{ source('sec', 'sec_companyfacts_flat') }}
    where ingest_date = (
        select max(ingest_date)
        from {{ source('sec', 'sec_companyfacts_flat') }}
    )
),

typed as (
    select
        ticker,
        cik,
        entity_name,
        taxonomy,
        tag,
        label,
        unit,
        cast(period_start as date)  as period_start,
        cast(period_end as date)    as period_end,
        value,
        fiscal_year                 as filing_fiscal_year,
        fiscal_period               as filing_fiscal_period,
        form,
        cast(filed as date)         as filed_date,
        accession,
        frame,
        cast(ingest_date as date)   as ingest_date
    from latest_snapshot
),

ranked as (
    select
        *,
        case when period_start is null then 'instant' else 'duration' end as period_type,
        date_diff('day', period_start, period_end) + 1 as period_days,
        -- The first filing to report a period is that period's own annual
        -- report, so its fiscal year label is the period's fiscal year
        first_value(filing_fiscal_year) over (
            partition by ticker, taxonomy, tag, unit, period_start, period_end
            order by filed_date asc, accession asc
        ) as original_filing_fiscal_year,
        row_number() over (
            partition by ticker, taxonomy, tag, unit, period_start, period_end
            order by filed_date desc, accession desc
        ) as row_rank
    from typed
)

select
    ticker,
    cik,
    entity_name,
    taxonomy,
    tag,
    label,
    unit,
    period_type,
    period_start,
    period_end,
    period_days,
    value,
    filing_fiscal_year,
    filing_fiscal_period,
    original_filing_fiscal_year,
    form,
    filed_date,
    accession,
    frame,
    ingest_date
from ranked
where row_rank = 1
