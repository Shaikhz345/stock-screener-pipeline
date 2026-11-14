"""Pull recent daily prices from Tiingo and save the raw data to S3."""
import argparse
import csv
import json
import os
import sys
from datetime import date, timedelta

import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

TIINGO_URL = "https://api.tiingo.com/tiingo/daily/{ticker}/prices"


def load_universe(path="config/universe.csv"):
    with open(path) as f:
        return [row["ticker"] for row in csv.DictReader(f)]


def fetch_prices(ticker, start_date, token):
    resp = requests.get(
        TIINGO_URL.format(ticker=ticker),
        headers={"Authorization": f"Token {token}"},
        params={"startDate": start_date},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7,
                        help="How many days back to pull")
    args = parser.parse_args()

    token = os.environ["TIINGO_API_KEY"]
    bucket = os.environ["S3_BUCKET"]
    s3 = boto3.client("s3")

    ingest_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=args.days)).isoformat()
    tickers = load_universe()

    print(f"Pulling {len(tickers)} tickers from {start_date} (ingest date {ingest_date})")
    failed = []
    for ticker in tickers:
        try:
            rows = fetch_prices(ticker, start_date, token)
        except requests.RequestException as e:
            print(f"  {ticker}: FAILED ({e})")
            failed.append(ticker)
            continue


        body = "\n".join(json.dumps({"ticker": ticker, **row}) for row in rows)
        key = f"raw/tiingo/daily_prices/ingest_date={ingest_date}/{ticker}.json"
        s3.put_object(Bucket=bucket, Key=key, Body=body,
                      ContentType="application/json")
        print(f"  {ticker}: {len(rows)} rows saved")

    print(f"\nDone: {len(tickers) - len(failed)} succeeded, {len(failed)} failed")
    if failed:
        print("Failed tickers:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()