import json
import os
from datetime import datetime

# Check JSON metadata
with open('public/data/ticker/CHAMBLFERT.NS.json') as f:
    data = json.load(f)

json_updated = data['meta'].get('last_updated')
print(f'JSON last updated: {json_updated}')

# Check CSV modification time
csv_path = 'public/data/raw/CHAMBLFERT_NS.csv'
if os.path.exists(csv_path):
    csv_mtime = os.path.getmtime(csv_path)
    csv_mtime_readable = datetime.fromtimestamp(csv_mtime)
    print(f'CSV last modified: {csv_mtime_readable}')

# Check live spot prices
with open('public/data/live/spot_prices.json') as f:
    live = json.load(f)
    chambl_live = live['spot_prices'].get('CHAMBLFERT.NS')
    if chambl_live:
        print(f'\nLive spot price data:')
        print(f'  Price: {chambl_live["spot_price"]}')
        print(f'  Timestamp: {chambl_live.get("timestamp")}')

# The real issue
print('\n=== THE REAL ISSUE ===')
print(f'JSON JSON spot_price field: {data["metrics"]["spot_price"]}')
print(f'Live spot price: {chambl_live["spot_price"] if chambl_live else "NOT FOUND"}')
print()
print('These should match! But they don\'t because:')
print('1. JSON was generated at 06:16:26 with Close price from that time')
print('2. Live spot is from Dec 1 at 19:15:19 (STALE!)')
print()
print('BOTH are STALE! We need fresh data!')
