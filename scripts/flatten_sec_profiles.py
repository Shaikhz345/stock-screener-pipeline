"""Extract one row per company from raw SEC submissions files, saved as Parquet in S3."""
import io
import json
import os

import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from dotenv import load_dotenv

load_dotenv()

RAW_PREFIX = "raw/sec/submissions/"
FLAT_PREFIX = "raw/sec/company_profiles_flat/"

SCHEMA = pa.schema([
    ("ticker", pa.string()),
    ("cik", pa.string()),
    ("entity_name", pa.string()),
    ("entity_type", pa.string()),
    ("sic", pa.string()),
    ("sic_description", pa.string()),
    ("fiscal_year_end", pa.string()),
    ("state_of_incorporation", pa.string()),
    ("listed_tickers", pa.string()),
    ("listed_exchanges", pa.string()),
])


def main():
    bucket = os.environ["S3_BUCKET"]
    s3 = boto3.client("s3")

    # Find the newest SEC load
    keys = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=RAW_PREFIX):
        keys += [o["Key"] for o in page.get("Contents", [])]
    latest = max(k.split("/")[3] for k in keys)
    latest_keys = sorted(k for k in keys if k.split("/")[3] == latest)

    rows = []
    for key in latest_keys:
        ticker = key.split("/")[-1].replace(".json", "")
        doc = json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
        rows.append({
            "ticker": ticker,
            "cik": str(doc.get("cik", "")).zfill(10),
            "entity_name": doc.get("name"),
            "entity_type": doc.get("entityType"),
            "sic": doc.get("sic"),
            "sic_description": doc.get("sicDescription"),
            "fiscal_year_end": doc.get("fiscalYearEnd"),
            "state_of_incorporation": doc.get("stateOfIncorporation"),
            "listed_tickers": ",".join(doc.get("tickers") or []),
            "listed_exchanges": ",".join(e or "" for e in (doc.get("exchanges") or [])),
        })

    # All 38 companies fit in one small file
    buffer = io.BytesIO()
    pq.write_table(pa.Table.from_pylist(rows, schema=SCHEMA), buffer, compression="snappy")
    out_key = f"{FLAT_PREFIX}{latest}/company_profiles.parquet"
    s3.put_object(Bucket=bucket, Key=out_key, Body=buffer.getvalue())

    print(f"Wrote {len(rows)} company profiles from {latest}\n")
    for r in rows:
        print(f"  {r['ticker']:<5} {r['sic']}  {r['entity_name']}  [{r['listed_exchanges']}]")


if __name__ == "__main__":
    main()     