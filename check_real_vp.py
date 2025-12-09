import json

data = json.load(open('public/data/ticker/LEMONTREE.json'))
spot = data['metrics']['spot_price']
vp = data['volumeProfile']

print(f"Spot Price: ₹{spot:.2f}")
print(f"\nVolume Profile Prices:")
print("Price\t\tVolume")
print("-" * 40)
for b in vp:
    print(f"₹{b['price']:.2f}\t\t{b['volume']:,}")
