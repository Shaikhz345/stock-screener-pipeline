-- One row per company per fiscal year with revenue, net income,
-- and diluted EPS, using the tag priorities in the sec_tag_map seed.

with tag_map as (
    select * from {{ ref('sec_tag_map') }}
),

annual_facts as (
    select
        f.ticker,
        f.period_start,
        f.period_end,
        f.original_filing_fiscal_year,
        f.value,
        f.tag,
        f.filed_date,
        m.metric,
        m.priority
    from {{ ref('stg_sec__company_facts') }} as f
    inner join tag_map as m
        on  f.taxonomy = m.taxonomy
        and f.tag      = m.tag
        and f.unit     = m.unit
    where f.period_type = 'duration'
      and f.period_days between 350 and 380
      and m.metric in ('revenue', 'net_income', 'eps_diluted')
),

best_tag as (
    select
        *,
        row_number() over (
            partition by ticker, metric, period_end
            order by priority
        ) as tag_rank
    from annual_facts
)

select
    ticker,
    max(original_filing_fiscal_year)                       as fiscal_year,
    min(period_start)                                      as fiscal_year_start,
    period_end                                             as fiscal_year_end,
    max(case when metric = 'revenue'     then value end)   as revenue,
    max(case when metric = 'net_income'  then value end)   as net_income,
    max(case when metric = 'eps_diluted' then value end)   as eps_diluted,
    max(case when metric = 'revenue'     then tag end)     as revenue_tag,
    max(filed_date)                                        as latest_filed_date
from best_tag
where tag_rank = 1
group by ticker, period_end
