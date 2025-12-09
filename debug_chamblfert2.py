import pandas as pd
import json

# Check the CSV data
df = pd.read_csv('public/data/raw/CHAMBLFERT_NS.csv', index_col=0)
print('CSV Data (last 5 rows):')
print(df.tail())
print()
print(f'CSV Date range: {df.index[0]} to {df.index[-1]}')
print(f'Latest close: {df.iloc[-1]["Close"]}')
print()

# Now check the JSON
with open('public/data/ticker/CHAMBLFERT.NS.json') as f:
    data = json.load(f)

print('=== PROBLEM ANALYSIS ===')
print(f'1. spotPrice field in metrics: {data["metrics"].get("spotPrice")}')
print(f'   This should be: 441.7 (from live spot_prices.json)')
print()
print(f'2. Volume Profile closes at: {data["volumeProfile"][-1]["price"]} (from CSV data)')
print(f'   This should align with spot price: 441.7')
print()
print(f'3. Orderbook centered at: {[x["price"] for x in data["orderbook"][:3]]}')
print()
print(f'4. Last candle close: {data["candles"][-1]["close"]}')
print()

# Check if the issue is that spotPrice field is missing
print('=== FIELDS IN METRICS ===')
print(list(data['metrics'].keys()))
