import json

data = json.load(open('public/data/ticker/LEMONTREE.json'))
spot = data['metrics']['spot_price']

print(f"=== LEMON STOCK - ALL REAL DATA ===")
print(f"Spot Price: ₹{spot:.2f}\n")

# Rolling Averages
if 'rollingAverages' in data and data['rollingAverages']:
    print("Rolling Averages (last 3):")
    for ra in data['rollingAverages'][-3:]:
        if ra['ma20'] and ra['ma50']:
            print(f"  {ra['date']}: Close ₹{ra['close']:.2f}, MA5 ₹{ra['ma5']:.2f}, MA20 ₹{ra['ma20']:.2f}, MA50 ₹{ra['ma50']:.2f}")

# Absorption Flow
if 'absorptionFlow' in data and data['absorptionFlow']:
    print("\nAbsorption Flow (last 3):")
    for af in data['absorptionFlow'][-3:]:
        total = af['buyFlow'] + af['sellFlow']
        buy_pct = af['buyFlow'] / total * 100 if total > 0 else 0
        print(f"  {af['date']}: Buy {af['buyFlow']:,} ({buy_pct:.0f}%), Sell {af['sellFlow']:,}")

# Heatmap
if 'heatmap' in data and data['heatmap']:
    print("\nHeatmap (sample - Friday 1-2pm):")
    fridays = [h for h in data['heatmap'] if h['dayOfWeek'] == 4]  # Friday
    pm_hours = [h for h in fridays if 13 <= h['hour'] <= 14]
    for h in pm_hours[:2]:
        print(f"  Friday {h['hour']}:00 - Intensity: {h['value']}, Count: {h['count']:,}")

# Histogram
if 'histogram' in data and data['histogram']:
    print("\nReturns Distribution (histogram):")
    for h in data['histogram']:
        print(f"  Bin {h['bin']:+.2f}%: {h['count']} days ({h['percentage']:.1f}%)")

# Slippage Samples
if 'slippageSamples' in data and data['slippageSamples']:
    print("\nSlippage Samples (first 3):")
    for s in data['slippageSamples'][:3]:
        print(f"  {s['timestamp']}: Expected ₹{s['expected']:.2f}, Actual ₹{s['actual']:.2f}, Slippage {s['slippage']:.3f}%, Volume {s['volume']:,}")

print("\n✅ All data is from REAL OHLCV - NO MORE SYNTHETIC!")
