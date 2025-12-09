import json

# Check the CHAMBLFERT JSON file
with open('public/data/ticker/CHAMBLFERT.NS.json') as f:
    data = json.load(f)

print('=== CHAMBLFERT.NS DATA CHECK ===')
spot = data['metrics'].get('spotPrice', 'MISSING')
print(f'Spot Price: {spot}')
print(f'Last Updated: {data["meta"].get("last_updated", "MISSING")}')
print()

# Check volume profile
vp = data.get('volumeProfile', [])
print(f'Volume Profile: {len(vp)} buckets')
if vp:
    print(f'  First: {vp[0]["price"]}')
    print(f'  Last: {vp[-1]["price"]}')
    print(f'  Range: {vp[0]["price"]} - {vp[-1]["price"]}')
    print(f'  Sample prices: {[v["price"] for v in vp[:5]]}')
print()

# Check candles
candles = data.get('candles', [])
print(f'Candles: {len(candles)} bars')
if candles:
    print(f'  Last 3 candles close: {[c["close"] for c in candles[-3:]]}')
print()

# Check orderbook
ob = data.get('orderbook', [])
print(f'Orderbook: {len(ob)} levels')
if ob:
    bids = [x for x in ob if x.get('side') == 'bid']
    asks = [x for x in ob if x.get('side') == 'ask']
    if bids:
        print(f'  Bids: {len(bids)} - Range: {bids[0]["price"]} - {bids[-1]["price"]}')
    if asks:
        print(f'  Asks: {len(asks)} - Range: {asks[0]["price"]} - {asks[-1]["price"]}')
print()

# Check rolling averages
ma = data.get('rollingAverages', [])
print(f'Rolling Averages: {len(ma)} data points')
if ma:
    print(f'  Last MA5/20/50: {ma[-1]}')
print()

# Check slippage
slippage = data.get('slippageSamples', [])
print(f'Slippage Samples: {len(slippage)} samples')
if slippage:
    print(f'  Sample prices: {[s.get("expectedPrice", s.get("price")) for s in slippage[:3]]}')
print()

# Check live spot price
print('=== LIVE SPOT PRICES ===')
with open('public/data/live/spot_prices.json') as f:
    live = json.load(f)
    if 'spot_prices' in live:
        chambl = live['spot_prices'].get('CHAMBLFERT.NS')
        if chambl:
            print(f'Live CHAMBLFERT spot: {chambl}')
