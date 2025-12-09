import json
import os

# Search for any JSON file with price ranges in the 2800-3600 range
ticker_dir = 'public/data/ticker'
found_mismatch = []

for f in os.listdir(ticker_dir):
    if not f.endswith('.json') or '_slippage' in f or '_monte' in f:
        continue
    try:
        with open(os.path.join(ticker_dir, f)) as fp:
            data = json.load(fp)
        
        spot = data['metrics'].get('spot_price', 0)
        if 'volumeProfile' in data and data['volumeProfile']:
            vp_low = data['volumeProfile'][0]['price']
            vp_high = data['volumeProfile'][-1]['price']
            
            # Check if there's a huge mismatch (5x or more difference)
            if spot > 0 and (vp_high / spot > 5 or spot / vp_high > 5):
                found_mismatch.append({
                    'ticker': f,
                    'spot': spot,
                    'vp_low': vp_low,
                    'vp_high': vp_high,
                    'ratio': vp_high / spot
                })
    except Exception as e:
        pass

print(f'Found {len(found_mismatch)} tickers with major mismatches:')
for m in sorted(found_mismatch, key=lambda x: x['ratio'], reverse=True)[:15]:
    print(f'  {m["ticker"]}: Spot ₹{m["spot"]:.0f}, VP ₹{m["vp_low"]:.0f}-{m["vp_high"]:.0f}, Ratio: {m["ratio"]:.1f}x')

if not found_mismatch:
    print('  (No major mismatches found)')
