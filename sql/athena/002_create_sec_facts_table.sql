-- 002: Flattened SEC company facts
-- One row per reported value, written as Parquet by scripts/flatten_sec_facts.py.

CREATE EXTERNAL TABLE IF NOT EXISTS stock_screener_raw.sec_companyfacts_flat (
  ticker         string,
  cik            string,
  entity_name    string,
  taxonomy       string,
  tag            string,
  label          string,
  unit           string,
  period_start   string,
  period_end     string,
  value          double,
  fiscal_year    bigint,
  fiscal_period  string,
  form           string,
  filed          string,
  accession      string,
  frame          string
)
PARTITIONED BY (ingest_date string)
STORED AS PARQUET
LOCATION 's3://zs-stock-screener-data/raw/sec/companyfacts_flat/';

-- Register the ingest_date folders. Rerun after new SEC loads.
MSCK REPAIR TABLE stock_screener_raw.sec_companyfacts_flat;
