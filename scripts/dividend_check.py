import csv
import os
from datetime import date, timedelta

import requests
from dotenv import load_dotenv

load_dotenv()
headers = {"Authorization": f"Token {os.environ['TIINGO_API_KEY']}"}
start = (date.today() - timedelta(days=365)).isoformat()

with open("config/universe.csv") as f:
    universe = list(csv.DictReader(f))

results = []
for row in universe:
    ticker = row["ticker"]
    url = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices"
    resp = requests.get(url, headers=headers, params={"startDate": start}, timeout=30)
    if resp.status_code != 200:
        print(f"{ticker}: error {resp.status_code}")
        continue
    prices = resp.json()
    if not prices:
        print(f"{ticker}: no data")
        continue

    # Add up the past year's dividends. Older ones are adjusted for any
    # later splits, so all amounts are in today's share terms.
    total_div = 0.0
    payments = 0
    split_factor = 1.0
    for day in reversed(prices):
        if day["divCash"] > 0:
            total_div += day["divCash"] / split_factor
            payments += 1
        split_factor *= day["splitFactor"]

    price = prices[-1]["close"]
    yield_pct = total_div / price * 100
    results.append((ticker, row["asset_type"], payments, total_div, price, yield_pct))

results.sort(key=lambda r: r[5], reverse=True)
print(f"\n{'Ticker':<7}{'Type':<7}{'Payments':>9}{'Div/yr':>10}{'Price':>10}{'Yield':>8}")
for t, a, n, d, p, y in results:
    print(f"{t:<7}{a:<7}{n:>9}{d:>10.2f}{p:>10.2f}{y:>7.2f}%")