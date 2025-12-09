import json
import os
from pathlib import Path
import random

# Get all ticker JSON files
ticker_dir = Path("public/data/ticker")
json_files = sorted(ticker_dir.glob("*.NS.json"))

print(f"Total stock JSON files: {len(json_files)}\n")

# Sample 15 random stocks
sample = random.sample(json_files, min(15, len(json_files)))

verdict_count = 0
no_verdict_count = 0
issues = []

for json_file in sample:
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        ticker = data.get('ticker', 'Unknown')
        verdict = data.get('metrics', {}).get('verdict', {})
        has_volume = len(data.get('volumeProfile', [])) > 0
        has_candles = len(data.get('candles', [])) > 0
        has_orderbook = len(data.get('orderbook', [])) > 0
        has_slippage = 'slippageExpectation' in data.get('metrics', {})
        has_spot = 'spot_price' in data.get('metrics', {})
        
        if verdict and verdict.get('direction'):
            verdict_count += 1
            status = "✅"
        else:
            no_verdict_count += 1
            status = "⚠️"
            issues.append(f"No verdict for {ticker}")
        
        print(f"{status} {ticker}")
        if verdict:
            print(f"   Verdict: {verdict.get('direction', 'NONE')} (Conf: {verdict.get('confidence', 0):.2f})")
        print(f"   Charts: VP={has_volume}, Candles={has_candles}, OB={has_orderbook}, Slip={has_slippage}, Spot={has_spot}")
        print()
    except Exception as e:
        issues.append(f"Error reading {json_file.name}: {e}")
        print(f"❌ {json_file.name}: {e}\n")

print("\n" + "="*60)
print(f"Sample Results: {verdict_count}/{len(sample)} have verdicts")
print(f"Issues found: {len(issues)}")
if issues:
    for issue in issues:
        print(f"  - {issue}")

# Also check all files for verdict coverage
print("\n" + "="*60)
print("Full scan of all stocks...")
all_verdicts = 0
all_issues = 0

for json_file in json_files:
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        verdict = data.get('metrics', {}).get('verdict', {})
        if verdict and verdict.get('direction'):
            all_verdicts += 1
        else:
            all_issues += 1
    except:
        all_issues += 1

print(f"✅ Stocks with verdicts: {all_verdicts}/{len(json_files)}")
print(f"❌ Stocks without verdicts: {all_issues}/{len(json_files)}")
print(f"Coverage: {(all_verdicts/len(json_files)*100):.1f}%")
