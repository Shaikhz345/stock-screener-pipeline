import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ["TIINGO_API_KEY"]
headers = {"Authorization": f"Token {api_key}"}

for ticker in ["AAPL", "SPY"]:
    url = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices"
    params = {"startDate": "2020-08-03", "endDate": "2020-09-04"}
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    rows = response.json()

    print(f"\n{ticker}: {len(rows)} trading days")
    for row in rows:
        if row["divCash"] > 0 or row["splitFactor"] != 1:
            print(row["date"][:10],
                  "| close:", row["close"],
                  "| adjClose:", round(row["adjClose"], 2),
                  "| dividend:", row["divCash"],
                  "| split:", row["splitFactor"])
