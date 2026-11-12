# 001: Price data source

**Status:** Accepted
**Date:** 2026-11-11

## Decision
Use the Tiingo free (Starter) plan for daily prices, dividends, and splits.

## Requirements
- Daily closing prices with 5+ years of history
- Dividend history with dates and amounts
- Split data or split-adjusted prices
- Covers stocks and ETFs
- Enough free calls for 50 stocks a day, plus a one-time backfill

## Options considered
| | Tiingo | Alpha Vantage | Financial Modeling Prep | Massive (Polygon) |
|---|---|---|---|---|
| Free calls | 1,000/day, 50/hour | 25/day | 250/day | No free stocks plan |
| Symbols | 500/month | Any | Many endpoints limited to sample tickers | n/a |
| History | 30+ years | Varies | 5 years | n/a |
| Dividends and splits | Yes, in the daily price call | Unclear on free tier | Sample tickers only | n/a |
| ETFs | Yes | Yes | Limited | n/a |

## Why Tiingo
One call per ticker returns raw and adjusted prices, the dividend paid
(divCash), and the split factor. Tested on AAPL's August 2020 dividend
and 4-for-1 split, and on SPY: both returned correctly.

## Trade-offs
- 50 requests/hour: fine for 50 stocks; 500 stocks will need the daily
  pull spread across several hours.
- 500 unique symbols/month: caps the universe at about 500 tickers.
- License is internal use only: raw data is never committed to this repo.

## Design rule from testing
Use adjClose for returns and 52-week ranges. Raw close shows splits as
fake crashes (AAPL: about $444 to $129 on 2020-08-31).

## Revisit if
- The universe grows past 500 tickers
- Free-tier limits change
- Data quality issues appear in testing
