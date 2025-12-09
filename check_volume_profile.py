import json

with open('public/data/ticker/LEMONTREE.NS.json') as f:
    data = json.load(f)

spot = data['metrics']['spot_price']
vp = data['analysis']['volumeProfile']

print(f"Spot Price: ₹{spot:.2f}")
print(f"\nVolume Profile Prices (first 10):")
for i, bucket in enumerate(vp[:10]):
    print(f"  {i+1}. Price: ₹{bucket['price']:.2f}, Volume: {bucket['volume']:,}")

print(f"\nPrice Range in Volume Profile:")
prices = [b['price'] for b in vp]
print(f"  Min: ₹{min(prices):.2f}")
print(f"  Max: ₹{max(prices):.2f}")
print(f"  Current Spot: ₹{spot:.2f}")
print(f"\nDifference:")
print(f"  Spot to Min: {((spot - min(prices)) / min(prices) * 100):.2f}%")
print(f"  Spot to Max: {((max(prices) - spot) / spot * 100):.2f}%")
