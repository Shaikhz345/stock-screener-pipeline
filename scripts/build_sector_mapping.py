"""Convert the Fama-French 12-industry SIC definitions into a CSV,
then preview which sector each stock falls into."""
import csv
import json
import os
import re

import boto3
from dotenv import load_dotenv

load_dotenv()

SOURCE = "reference/Siccodes12.txt"
OUTPUT = "config/sector_mapping.csv"

# A header line looks like: " 1 NoDur  Consumer NonDurables -- Food, ..."
HEADER = re.compile(r"^\s*(\d{1,2})\s+([A-Za-z]+)\s+(.+?)\s*$")
# A range line looks like: "          0100-0999"
RANGE = re.compile(r"^\s*(\d{4})-(\d{4})")


def parse_definitions(path):
    sectors, ranges, current = [], [], None
    with open(path, encoding="latin-1") as f:
        for line in f:
            r = RANGE.match(line)
            if r and current:
                ranges.append({**current,
                               "sic_start": int(r.group(1)),
                               "sic_end": int(r.group(2))})
                continue
            h = HEADER.match(line)
            if h:
                current = {"sector_code": int(h.group(1)),
                           "sector_short": h.group(2),
                           "sector_name": h.group(3)}
                sectors.append(current)
    return sectors, ranges


def sector_for(sic, ranges, default):
    for row in ranges:
        if row["sic_start"] <= sic <= row["sic_end"]:
            return row["sector_short"]
    return default


def main():
    sectors, ranges = parse_definitions(SOURCE)

    # Sectors with no SIC ranges (Fama-French's "Other") catch everything else
    with_ranges = {r["sector_short"] for r in ranges}
    default = next(s["sector_short"] for s in sectors
                   if s["sector_short"] not in with_ranges)

    with open(OUTPUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["sector_code", "sector_short",
                                               "sector_name", "sic_start", "sic_end"])
        writer.writeheader()
        writer.writerows(ranges)
    print(f"Wrote {len(ranges)} SIC ranges across {len(sectors)} sectors to {OUTPUT}")
    print(f"Codes outside every range default to: {default}\n")

    # Preview: read each stock's SIC code from the latest SEC load in S3
    s3 = boto3.client("s3")
    bucket = os.environ["S3_BUCKET"]
    prefix = "raw/sec/submissions/"
    keys = [o["Key"] for o in
            s3.list_objects_v2(Bucket=bucket, Prefix=prefix).get("Contents", [])]
    latest = max(k.split("/")[3] for k in keys)
    latest_keys = [k for k in keys if k.split("/")[3] == latest]

    preview = []
    for key in latest_keys:
        profile = json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())
        ticker = key.split("/")[-1].replace(".json", "")
        sic = int(profile["sic"])
        preview.append((sector_for(sic, ranges, default), ticker, sic,
                        profile.get("sicDescription", "")))

    for sector, ticker, sic, desc in sorted(preview):
        print(f"  {sector:<6} {ticker:<5} {sic}  {desc}")


if __name__ == "__main__":
    main()