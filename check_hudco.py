import json

# Check HUDCO (the most corrupted one)
with open('public/data/ticker/HUDCO.NS.json') as f:
    data = json.load(f)

print('HUDCO.NS Volume Profile (first 5 and last 5):')
vp = data['volumeProfile']
for item in vp[:5]:
    print(f'  Price: ₹{item["price"]:.0f}, Count: {item["count"]}')
print('  ...')
for item in vp[-5:]:
    print(f'  Price: ₹{item["price"]:.0f}, Count: {item["count"]}')

print(f'\nSpot Price: ₹{data["metrics"]["spot_price"]:.0f}')
print(f'Candles range: ₹{min([c["low"] for c in data["candles"]]):.0f} - ₹{max([c["high"] for c in data["candles"]]):.0f}')
