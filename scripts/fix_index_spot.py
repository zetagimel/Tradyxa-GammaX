#!/usr/bin/env python3
"""Fix index spot prices from CSVs."""
import json
import pandas as pd

# NIFTY
df = pd.read_csv('public/data/raw/NSEI.csv', index_col=0, parse_dates=True)
close = float(df['Close'].iloc[-1])
print(f'NSEI latest close: {close}')

for jf in ['public/data/ticker/NIFTY.json', 'public/data/ticker/^NSEI.json']:
    try:
        with open(jf, 'r') as f:
            d = json.load(f)
        d['metrics']['spot_price'] = close
        with open(jf, 'w') as f:
            json.dump(d, f, indent=2)
        print(f'Updated {jf}')
    except Exception as e:
        print(f'Skip {jf}: {e}')

# BANKNIFTY
df2 = pd.read_csv('public/data/raw/NSEBANK.csv', index_col=0, parse_dates=True)
close2 = float(df2['Close'].iloc[-1])
print(f'NSEBANK latest close: {close2}')

for jf in ['public/data/ticker/BANKNIFTY.json', 'public/data/ticker/^NSEBANK.json']:
    try:
        with open(jf, 'r') as f:
            d = json.load(f)
        d['metrics']['spot_price'] = close2
        with open(jf, 'w') as f:
            json.dump(d, f, indent=2)
        print(f'Updated {jf}')
    except Exception as e:
        print(f'Skip {jf}: {e}')

print('Done!')
