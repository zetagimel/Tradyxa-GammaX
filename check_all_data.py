import json

data = json.load(open('public/data/ticker/LEMONTREE.json'))
spot = data['metrics']['spot_price']

print(f"=== LEMON Stock Data ===")
print(f"Spot Price: ₹{spot:.2f}\n")

# Check candles
if 'candles' in data and data['candles']:
    print("Candles (last 5):")
    for c in data['candles'][-5:]:
        print(f"  {c['date']}: Open ₹{c['open']:.2f}, High ₹{c['high']:.2f}, Low ₹{c['low']:.2f}, Close ₹{c['close']:.2f}")

# Check Bollinger Bands
if 'bollingerBands' in data and data['bollingerBands']:
    print("\nBollinger Bands (last 5):")
    for b in data['bollingerBands'][-5:]:
        if b['sma']:
            print(f"  {b['date']}: Close ₹{b['close']:.2f}, SMA ₹{b['sma']:.2f}, Upper ₹{b['upper']:.2f}, Lower ₹{b['lower']:.2f}")

# Check orderbook
if 'orderbook' in data and data['orderbook']:
    print("\nOrderbook (around current price):")
    ob = data['orderbook']
    # Find entries near spot price
    mid_idx = len(ob) // 2
    for o in ob[mid_idx-3:mid_idx+4]:
        bid_str = f"Bid: {o['bidQty']:,}" if o['bidQty'] > 0 else ""
        ask_str = f"Ask: {o['askQty']:,}" if o['askQty'] > 0 else ""
        print(f"  ₹{o['price']:.2f}: {bid_str} {ask_str}")

# Check volume profile
if 'volumeProfile' in data and data['volumeProfile']:
    print("\nVolume Profile (range):")
    vp = data['volumeProfile']
    print(f"  Min price: ₹{vp[0]['price']:.2f}")
    print(f"  Max price: ₹{vp[-1]['price']:.2f}")
    print(f"  Spot price: ₹{spot:.2f}")
    print(f"  Range check: {vp[0]['price'] <= spot <= vp[-1]['price']}")
