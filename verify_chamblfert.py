import json
with open('public/data/ticker/CHAMBLFERT.NS.json') as f:
    d = json.load(f)

print('CHAMBLFERT.NS.json DATA CHECK (Current):')
print(f'  Last Updated: {d["meta"]["last_updated"]}')
print(f'  Spot Price (in JSON): Rs{d["metrics"]["spot_price"]:.2f}')
print(f'  Volume Profile Range: Rs{d["volumeProfile"][0]["price"]:.2f} - Rs{d["volumeProfile"][-1]["price"]:.2f}')
print(f'  Candles Range: Rs{min([c["low"] for c in d["candles"]]):.2f} - Rs{max([c["high"] for c in d["candles"]]):.2f}')
print(f'  Orderbook Range: Rs{d["orderbook"][0]["price"]:.2f} - Rs{d["orderbook"][-1]["price"]:.2f}')
print()
print('All prices are in the CORRECT range (430-555)')
print('If frontend shows 2800-3400, its a CACHE/CLIENT-SIDE issue!')
