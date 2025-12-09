import json
import os

# Check a random stock
stock_file = 'public/data/ticker/ADANIPORTS.NS.json'
with open(stock_file) as f:
    data = json.load(f)

charts = data.get('charts', {})
print('Available charts in ADANIPORTS.NS.json:')
for chart_name in charts.keys():
    print(f'  ✓ {chart_name}')

print(f'\nTotal charts: {len(charts)}')
print(f'\nMetrics sample: {list(data.get("metrics", {}).keys())[:15]}')
print(f'Has verdict: {"verdict" in data}')

# Check what we need
all_keys = list(data.keys())
print('\n\nAll keys in JSON:')
for key in all_keys:
    if key not in ['meta', 'metrics', 'features_head']:
        value = data[key]
        is_list = isinstance(value, list)
        length = len(value) if is_list else 'N/A'
        print(f'  {key}: {length} items' if is_list else f'  {key}')
