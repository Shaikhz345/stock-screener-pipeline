# 004: Sector mapping

**Status:** Accepted
**Date:** 2026-11-14

## Decision
Map SIC codes to sectors using the Fama-French 12-industry definitions
(reference/Siccodes12.txt, from the Kenneth French Data Library),
converted to config/sector_mapping.csv. A ticker-level override file
(config/sector_overrides.csv) corrects misleading assignments.

## Why Fama-French
- Free, widely used in finance research, and based on SIC codes the SEC already provides
- Commercial standards like GICS are licensed and not free

## Findings from the first mapping
- 9 of 38 stocks fell into "Other," including railroads, trucking, waste, and payments
- Fama-French 12 has no transportation sector
- SIC codes misplace some companies (V and MA in business services, MMM and MSA in healthcare)
- Several sectors had only one stock

## Overrides
- V, MA to Money; MMM, MSA to Manuf; PG, CL, CHD to NoDur
- New Trans sector for CSX, UNP, UPS, SAIA
- Each override records its reason in the file

## Screener rule
pe_vs_sector is only calculated when a sector has at least 3 stocks with
positive earnings; otherwise it is blank

## Trade-offs
- Overrides are manual and must be reviewed when tickers are added
- Small sectors (Chems, Durbl, Money) get no P/E comparison until the universe grows
