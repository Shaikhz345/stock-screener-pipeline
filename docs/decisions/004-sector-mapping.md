# 004: Sector mapping

**Status:** Accepted
**Date:** 2026-11-14

## Decision
Map SIC codes to sectors using the Fama-French 12-industry definitions
(reference/Siccodes12.txt, from the Kenneth French Data Library),
converted to config/sector_mapping.csv. Override files correct
misleading assignments.

## Why Fama-French
- Free, widely used in finance research, and based on SIC codes the SEC already provides
- Commercial standards like GICS are licensed and not free

## Findings from the first mapping
- 9 of 38 stocks fell into "Other," including railroads, trucking, waste, and payments
- Fama-French 12 has no transportation sector
- SIC codes misplace some companies (V and MA in business services, MMM and MSA in healthcare)
- Several sectors had only one stock

## Overrides
Applied in priority order: ticker override, then rule override,
then Fama-French, then the default (Other). A sector_source column
records which one applied.
- Rule override (config/sector_rule_overrides.csv): SIC 4000-4799 to a
  new Trans sector (CSX, UNP, UPS, SAIA)
- Ticker overrides (config/sector_overrides.csv), only for true exceptions:
  V, MA to Money; MMM, MSA to Manuf; PG, CL, CHD to NoDur
  (a rule on SIC 2840 would wrongly move ECL)
- Each override records its reason

## Screener rule
pe_vs_sector is only calculated when a sector has at least 3 stocks with
positive earnings; otherwise it is blank

## Quality checks (built in Step 11)
- Flag stocks that fell through to the default sector, sorted by market cap
- Fail if more than 10% of stocks land in Other
- Known-answer test: V and MA must map to Money, AAPL to BusEq

## Trade-offs
- Overrides are manual and must be reviewed when tickers are added
- Small sectors (Chems, Durbl, Money) get no P/E comparison until the universe grows
