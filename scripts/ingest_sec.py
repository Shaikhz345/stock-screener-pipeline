"""Pull company profiles and financial facts from SEC EDGAR and save the raw data to S3."""
import csv
import os
import sys
import time
from collections import defaultdict
from datetime import date

import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"


def load_stocks(path="dbt/seeds/universe.csv"):
    with open(path) as f:
        return [row["ticker"] for row in csv.DictReader(f)
                if row["asset_type"] == "Stock"]


def load_cik_history(path="dbt/seeds/cik_history.csv"):
    """Every CIK a ticker has used, for companies whose SEC registration changed."""
    history = defaultdict(list)
    with open(path) as f:
        for row in csv.DictReader(f):
            history[row["ticker"]].append(row["cik"].zfill(10))
    return history


def get_json(session, url):
    time.sleep(0.2)  # stay well under the SEC's limit of 10 requests per second
    resp = session.get(url, timeout=60)
    resp.raise_for_status()
    return resp.json(), resp.content


def main():
    bucket = os.environ["S3_BUCKET"]
    s3 = boto3.client("s3")
    session = requests.Session()
    session.headers["User-Agent"] = os.environ["SEC_USER_AGENT"]
    ingest_date = date.today().isoformat()

    def save(folder, name, content):
        key = f"raw/sec/{folder}/ingest_date={ingest_date}/{name}.json"
        s3.put_object(Bucket=bucket, Key=key, Body=content,
                      ContentType="application/json")

    # 1. Ticker -> current CIK lookup (the SEC pads CIKs to 10 digits)
    lookup, lookup_raw = get_json(session, TICKERS_URL)
    save("company_tickers", "company_tickers", lookup_raw)
    cik_by_ticker = {row["ticker"]: str(row["cik_str"]).zfill(10)
                     for row in lookup.values()}
    cik_history = load_cik_history()

    stocks = load_stocks()
    print(f"Pulling SEC data for {len(stocks)} stocks (ingest date {ingest_date})\n")
    failed = []
    for ticker in stocks:
        current_cik = cik_by_ticker.get(ticker)
        if not current_cik:
            print(f"  {ticker}: FAILED (not in SEC ticker file)")
            failed.append(ticker)
            continue

        # The current CIK plus any earlier ones from cik_history.csv
        all_ciks = sorted(set([current_cik] + cik_history.get(ticker, [])))

        try:
            # Profile: current registration only (one row per company)
            profile, profile_raw = get_json(session, SUBMISSIONS_URL.format(cik=current_cik))
            save("submissions", ticker, profile_raw)

            # Facts: every registration, so history isn't lost
            for cik in all_ciks:
                facts, facts_raw = get_json(session, FACTS_URL.format(cik=cik))
                save("companyfacts", f"{ticker}__{cik}", facts_raw)
        except requests.RequestException as e:
            print(f"  {ticker}: FAILED ({e})")
            failed.append(ticker)
            continue

        note = f" | {len(all_ciks)} CIKs" if len(all_ciks) > 1 else ""
        print(f"  {ticker}: SIC {profile.get('sic')} {profile.get('sicDescription')} "
              f"| FY ends {profile.get('fiscalYearEnd')}{note}")

    print(f"\nDone: {len(stocks) - len(failed)} succeeded, {len(failed)} failed")
    if failed:
        print("Failed tickers:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
