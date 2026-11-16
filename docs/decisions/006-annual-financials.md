# 006: Annual financials

**Status:** Accepted
**Date:** 2026-11-15

## Decision
int_sec__annual_financials builds one row per company per fiscal year with
revenue, net income, and diluted EPS from SEC company facts.

## How numbers are chosen
- A seed (sec_tag_map.csv) lists which SEC tags count as each metric, with
  a priority when a company reports more than one
- Only full-year figures are used: duration periods of 350 to 380 days,
  which covers 52-week and 53-week fiscal years
- revenue_tag records which tag was used, so choices can be audited

## Fiscal year labels
- The SEC's fiscal year field describes the filing, not the period
- Companies name fiscal years differently: Nvidia by the year a period
  ends, Home Depot by the year it starts
- Each period is first reported in its own annual report, so the fiscal
  year of the earliest filing is the period's true fiscal year
  (original_filing_fiscal_year in staging)

## Companies whose SEC registration changed
- ExxonMobil moved to a new holding company with a new CIK in 2026; its
  history stayed under the old CIK
- A seed (cik_history.csv) lists every CIK a ticker has used. Financial
  facts are pulled for all of them and combined under one ticker
- Caught by a coverage check: XOM was missing from the first build

## Known gaps and decisions
- Visa reports EPS by share class only, so eps_diluted is blank for V.
  Decision: P/E will be calculated as market cap / net income for every
  company. eps_diluted is kept as a cross-check
- TSM is excluded (IFRS and New Taiwan dollars), per decision 003
- Periods first reported before a company's earliest SEC data may carry
  a later fiscal year label; this only affects the oldest years

## Verified (2026-11-15)
- 37 companies (all stocks except TSM)
- Fiscal year labels correct for AAPL, NVDA, HD, and JNJ
- XOM history restored from its predecessor CIK