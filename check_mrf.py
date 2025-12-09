import json

with open('public/data/ticker/MRF.NS.json') as f:
    d = json.load(f)

print('=== MRF.NS DATA CHECK ===')
print(f'Last Updated: {d["meta"]["last_updated"]}')
print(f'Spot Price (in JSON): Rs{d["metrics"]["spot_price"]:.2f}')
print(f'Volume Profile Range: Rs{d["volumeProfile"][0]["price"]:.2f} - Rs{d["volumeProfile"][-1]["price"]:.2f}')
print(f'Candles Range: Rs{min([c["low"] for c in d["candles"]]):.2f} - Rs{max([c["high"] for c in d["candles"]]):.2f}')
print(f'Orderbook Range: Rs{d["orderbook"][0]["price"]:.2f} - Rs{d["orderbook"][-1]["price"]:.2f}')
print()

# Check live spot
with open('public/data/live/spot_prices.json') as f:
    live = json.load(f)
    mrf_live = live['spot_prices'].get('MRF.NS')
    if mrf_live:
        print(f'Live MRF spot: Rs{mrf_live["spot_price"]:.2f}')
        print(f'Live timestamp: {mrf_live.get("timestamp")}')

print()
print(f'PROBLEM: JSON from {d["meta"]["last_updated"]} is STALE!')
print('Spot price changed during the day but tiles are STATIC!')
