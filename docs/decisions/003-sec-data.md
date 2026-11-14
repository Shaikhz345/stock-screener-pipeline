# 003: SEC company data

**Status:** Accepted
**Date:** 2026-11-14

## Decision
Pull company profiles (submissions API) and financial facts (company facts API)
from SEC EDGAR for the 38 stocks, saved raw to S3. ETFs are skipped.

## Findings from the first load
- 15 of 38 stocks have non-December fiscal years
- Several use week-based fiscal years whose end date shifts yearly
  (AAPL, CSCO, INTC, MLI, JNJ). JNJ's current fiscal year ends Jan 3
- The submissions fiscalYearEnd field is only the latest value, so fiscal
  year start and end dates will come from period dates in the financial facts
- TSM reports under IFRS (ifrs-full) in New Taiwan dollars, and one US
  share (ADR) represents 5 Taiwan shares
- Some SIC codes are misleading: V and MA are 7389 Business Services,
  MMM is 3841 Surgical Instruments
- Only three label sets are needed: us-gaap, ifrs-full, and dei

## Decisions
- TSM: prices load normally; fundamentals (revenue, earnings, P/E) are left
  blank and flagged in version one. Currency and ADR conversion is a
  version-two item
- Sector mapping will include a manual override file for misleading SIC codes

## Trade-offs
- TSM has no P/E or revenue columns until version two
- Raw files are large and deeply nested; flattening happens in a later step
