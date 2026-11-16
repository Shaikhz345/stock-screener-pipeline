"""Flatten raw SEC company facts into one row per reported value, saved as Parquet in S3."""
import io
import json
import os

import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from dotenv import load_dotenv

load_dotenv()

RAW_PREFIX = "raw/sec/companyfacts/"
FLAT_PREFIX = "raw/sec/companyfacts_flat/"

# A fixed schema keeps column types identical across every company's file
SCHEMA = pa.schema([
    ("ticker", pa.string()),
    ("cik", pa.string()),
    ("entity_name", pa.string()),
    ("taxonomy", pa.string()),
    ("tag", pa.string()),
    ("label", pa.string()),
    ("unit", pa.string()),
    ("period_start", pa.string()),
    ("period_end", pa.string()),
    ("value", pa.float64()),
    ("fiscal_year", pa.int64()),
    ("fiscal_period", pa.string()),
    ("form", pa.string()),
    ("filed", pa.string()),
    ("accession", pa.string()),
    ("frame", pa.string()),
])


def flatten(ticker, doc):
    rows = []
    for taxonomy, tags in doc.get("facts", {}).items():
        for tag, info in tags.items():
            for unit, facts in info.get("units", {}).items():
                for f in facts:
                    rows.append({
                        "ticker": ticker,
                        "cik": str(doc.get("cik", "")).zfill(10),
                        "entity_name": doc.get("entityName"),
                        "taxonomy": taxonomy,
                        "tag": tag,
                        "label": info.get("label"),
                        "unit": unit,
                        "period_start": f.get("start"),
                        "period_end": f.get("end"),
                        "value": float(f["val"]) if f.get("val") is not None else None,
                        "fiscal_year": f.get("fy"),
                        "fiscal_period": f.get("fp"),
                        "form": f.get("form"),
                        "filed": f.get("filed"),
                        "accession": f.get("accn"),
                        "frame": f.get("frame"),
                    })
    return rows


def main():
    bucket = os.environ["S3_BUCKET"]
    s3 = boto3.client("s3")

    # Find the newest SEC load
    keys = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=RAW_PREFIX):
        keys += [o["Key"] for o in page.get("Contents", [])]
    latest = max(k.split("/")[3] for k in keys)
    latest_keys = sorted(k for k in keys if k.split("/")[3] == latest)
    print(f"Flattening {len(latest_keys)} files from {latest}\n")

    total = 0
    for key in latest_keys:
        stem = key.split("/")[-1].replace(".json", "")
        ticker = stem.split("__")[0]
        doc = json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
        rows = flatten(ticker, doc)

        buffer = io.BytesIO()
        pq.write_table(pa.Table.from_pylist(rows, schema=SCHEMA), buffer,
                       compression="snappy")
        out_key = f"{FLAT_PREFIX}{latest}/{stem}.parquet"
        s3.put_object(Bucket=bucket, Key=out_key, Body=buffer.getvalue())

        total += len(rows)
        print(f"  {ticker}: {len(rows):,} facts, {buffer.tell() / 1_000_000:.1f} MB")

    print(f"\nDone: {total:,} facts across {len(latest_keys)} companies")


if __name__ == "__main__":
    main()