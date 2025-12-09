import json

# Check a stock that you're testing
with open('public/data/ticker/ADANIPORTS.NS.json') as f:
    data = json.load(f)

print("Keys in JSON:")
print(list(data.keys()))

print("\n\nData structure check:")
print(f"volumeProfile exists: {'volumeProfile' in data}")
print(f"volumeProfile length: {len(data.get('volumeProfile', []))}")
print(f"volumeProfile sample: {data.get('volumeProfile', [])[:2] if data.get('volumeProfile') else 'EMPTY'}")

print(f"\ncandles exists: {'candles' in data}")
print(f"candles length: {len(data.get('candles', []))}")
print(f"candles sample: {data.get('candles', [])[:2] if data.get('candles') else 'EMPTY'}")

print(f"\norderbook exists: {'orderbook' in data}")
print(f"orderbook length: {len(data.get('orderbook', []))}")
print(f"orderbook sample: {data.get('orderbook', [])[:2] if data.get('orderbook') else 'EMPTY'}")

print(f"\nbollingerBands exists: {'bollingerBands' in data}")
print(f"bollingerBands length: {len(data.get('bollingerBands', []))}")

print(f"\nrollingAverages exists: {'rollingAverages' in data}")
print(f"rollingAverages length: {len(data.get('rollingAverages', []))}")

print(f"\nabsorptionFlow exists: {'absorptionFlow' in data}")
print(f"absorptionFlow length: {len(data.get('absorptionFlow', []))}")

print(f"\nheatmap exists: {'heatmap' in data}")
print(f"heatmap length: {len(data.get('heatmap', []))}")

print(f"\nhistogram exists: {'histogram' in data}")
print(f"histogram length: {len(data.get('histogram', []))}")

print(f"\nslippageSamples exists: {'slippageSamples' in data}")
print(f"slippageSamples length: {len(data.get('slippageSamples', []))}")
