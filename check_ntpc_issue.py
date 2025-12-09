import pandas as pd
import json

# Check NTPC CSV
csv_path = 'public/data/raw/NTPC_NS.csv'
df = pd.read_csv(csv_path)
print('=== NTPC CSV DATA (Last 5 rows) ===')
print(df[['Date', 'Close']].tail(5))
print(f'\nLatest Close: ₹{df["Close"].iloc[-1]:.2f}')
print(f'60-day Low: ₹{df["Low"].tail(60).min():.2f}')
print(f'60-day High: ₹{df["High"].tail(60).max():.2f}')
print(f'CSV Min ever: ₹{df["Low"].min():.2f}')
print(f'CSV Max ever: ₹{df["High"].max():.2f}')

# Check JSON  
json_path = 'public/data/ticker/NTPC.NS.json'
try:
    with open(json_path) as f:
        data = json.load(f)
    print(f'\n=== NTPC JSON (CURRENT) ===')
    print(f'Last Updated: {data["meta"]["last_updated"]}')
    print(f'Spot in JSON: ₹{data["metrics"]["spot_price"]:.2f}')
    print(f'Volume Profile Range: ₹{data["volumeProfile"][0]["price"]:.0f} - ₹{data["volumeProfile"][-1]["price"]:.0f}')
    candles = data["candles"]
    print(f'Candles: {len(candles)} records')
    print(f'  First: ₹{candles[0]["high"]:.0f} (date: {candles[0].get("date", "N/A")})')
    print(f'  Last: ₹{candles[-1]["high"]:.0f} (date: {candles[-1].get("date", "N/A")})')
    print(f'  Range: ₹{min([c["low"] for c in candles]):.0f} - ₹{max([c["high"] for c in candles]):.0f}')
    
    print(f'\n🔴 ISSUE IDENTIFIED:')
    print(f'  JSON shows range: ₹{data["volumeProfile"][0]["price"]:.0f} - ₹{data["volumeProfile"][-1]["price"]:.0f}')
    print(f'  But CSV 60-day range: ₹{df["Low"].tail(60).min():.0f} - ₹{df["High"].tail(60).max():.0f}')
    print(f'  Current spot should be: ₹{df["Close"].iloc[-1]:.2f}')
    print(f'  But JSON shows: ₹{data["metrics"]["spot_price"]:.2f}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
