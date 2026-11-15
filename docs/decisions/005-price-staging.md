# 005: Price staging and adjusted prices

**Status:** Accepted
**Date:** 2026-11-15

## Decision
stg_tiingo__daily_prices combines the daily and backfill raw tables
and keeps one row per ticker per trading day. Adjusted prices will be
calculated in dbt from raw columns, not taken from the vendor.

## Deduplication rule
- Group copies by ticker and trading date
- Keep the newest ingest_date
- Tie-breaker for copies pulled the same day: prefer the daily load
- The rule is fixed so results never change between runs

## Why calculate adjusted prices ourselves
- Tiingo's adjClose is recalculated after every new split or dividend
- Daily runs only re-pull 7 days, so older rows would keep outdated
  adjustments, leaving the history on mixed bases
- close, divCash, and splitFactor never change, so overlapping copies
  never conflict
- Recalculating the full history on every run keeps it consistent
- Tiingo's value is kept as vendor_adj_close, only to test our calculation

## Verified on first run (2026-11-15)
- 114,678 rows, matching the backfill total
- 0 duplicate ticker-date pairs
- 300 rows from daily loads (50 tickers x 6 days), 114,378 from backfill
