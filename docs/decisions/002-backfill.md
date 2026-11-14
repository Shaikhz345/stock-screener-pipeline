# 002: Price history backfill

**Status:** Accepted
**Date:** 2026-11-13

## Decision
Backfill 10 years of daily prices for all 50 tickers, stored in a
separate raw folder from the daily loads.

## Why 10 years
- Covers 52-week ranges, dividend yield, and dividend growth streaks up to 10 years
- Includes real edge cases: the 2020 crash, AAPL/NVDA/TSLA splits, INTC's dividend suspension
- Same API cost as a daily run: one call per ticker returns the full range

## Why a separate folder
- Daily runs and one-time history loads are different load types
- A backfill can be rerun without touching daily data
- dbt staging combines both and keeps one row per ticker per day

## Results (2026-11-13)
- 50 tickers, 114,678 rows, 0 failures
- 41 tickers have the full 2,514 trading days
- Shorter histories: SNOW (IPO 2020), newer ETFs like SPTE, MNZL (248 days), AMGR (101 days)
- MNZL and AMGR have less than 52 weeks of data, so 52-week columns must handle missing history

## Trade-offs
- Dividend growth streaks are capped at 10 years ("10+")
- Overlapping days between folders must be deduplicated in staging
