-- 001: Raw Tiingo price tables
-- Defines Athena tables over the raw JSON files in S3.
-- External tables: dropping them never deletes the S3 data.

-- Database for the raw layer
CREATE DATABASE IF NOT EXISTS stock_screener_raw;

-- Daily runs (7-day lookback)
CREATE EXTERNAL TABLE IF NOT EXISTS stock_screener_raw.tiingo_daily_prices (
  ticker       string,
  `date`       string,
  open         double,
  high         double,
  low          double,
  close        double,
  volume       double,
  adjopen      double,
  adjhigh      double,
  adjlow       double,
  adjclose     double,
  adjvolume    double,
  divcash      double,
  splitfactor  double
)
PARTITIONED BY (ingest_date string)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://zs-stock-screener-data/raw/tiingo/daily_prices/';

-- One-time 10-year backfill
CREATE EXTERNAL TABLE IF NOT EXISTS stock_screener_raw.tiingo_daily_prices_backfill (
  ticker       string,
  `date`       string,
  open         double,
  high         double,
  low          double,
  close        double,
  volume       double,
  adjopen      double,
  adjhigh      double,
  adjlow       double,
  adjclose     double,
  adjvolume    double,
  divcash      double,
  splitfactor  double
)
PARTITIONED BY (ingest_date string)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://zs-stock-screener-data/raw/tiingo/daily_prices_backfill/';

-- Register the ingest_date folders as partitions.
-- Rerun after new date folders are added.
MSCK REPAIR TABLE stock_screener_raw.tiingo_daily_prices;
MSCK REPAIR TABLE stock_screener_raw.tiingo_daily_prices_backfill;