-- 003: SEC company profiles
-- One row per company, written as Parquet by scripts/flatten_sec_profiles.py.

CREATE EXTERNAL TABLE IF NOT EXISTS stock_screener_raw.sec_company_profiles_flat (
  ticker                  string,
  cik                     string,
  entity_name             string,
  entity_type             string,
  sic                     string,
  sic_description         string,
  fiscal_year_end         string,
  state_of_incorporation  string,
  listed_tickers          string,
  listed_exchanges        string
)
PARTITIONED BY (ingest_date string)
STORED AS PARQUET
LOCATION 's3://zs-stock-screener-data/raw/sec/company_profiles_flat/';

-- Register the ingest_date folders. Rerun after new SEC loads.
MSCK REPAIR TABLE stock_screener_raw.sec_company_profiles_flat;
