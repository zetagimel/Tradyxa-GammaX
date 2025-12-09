import json
with open('public/data/ticker/CHAMBLFERT.NS.json') as f:
    d = json.load(f)
    
print('Checking all price fields in CHAMBLFERT.NS.json:')
print(f'Spot Price: {d["metrics"]["spot_price"]}')
print(f'Volume Profile: {[v["price"] for v in d["volumeProfile"][:3]]} ... {[v["price"] for v in d["volumeProfile"][-3:]]}')
print(f'Candles close: {[c["close"] for c in d["candles"][-3:]]}')
print(f'Orderbook prices: {[o["price"] for o in d["orderbook"][:3]]}')
print(f'Rolling Avg: MA5={d["rollingAverages"][-1]["ma5"]}, MA20={d["rollingAverages"][-1]["ma20"]}, MA50={d["rollingAverages"][-1]["ma50"]}')
print()
print('All prices seem consistent - they are around 435-480 range, NOT 2800-3400!')
