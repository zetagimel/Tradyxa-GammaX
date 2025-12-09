import json
import os

# Find which stocks have prices in the 2800-3400 range
high_price_tickers = []

for filename in os.listdir('public/data/ticker'):
    if not filename.endswith('.json') or '_slippage' in filename:
        continue
    
    filepath = os.path.join('public/data/ticker', filename)
    try:
        with open(filepath) as f:
            data = json.load(f)
            vp = data.get('volumeProfile', [])
            if vp and vp[-1]['price'] > 2000:
                avg_price = (vp[0]['price'] + vp[-1]['price']) / 2
                high_price_tickers.append((filename, vp[0]['price'], vp[-1]['price'], avg_price))
    except:
        pass

# Sort by price
high_price_tickers.sort(key=lambda x: x[3], reverse=True)

print("Tickers with prices > 2000:")
for ticker, low, high, avg in high_price_tickers[:15]:
    print(f"  {ticker}: ₹{low:.0f} - ₹{high:.0f} (avg ₹{avg:.0f})")
