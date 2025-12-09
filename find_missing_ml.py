import json
from pathlib import Path

ticker_dir = Path("public/data/ticker")
json_files = sorted(ticker_dir.glob("*.NS.json"))

print("Checking for missing ML Regime labels...\n")

for json_file in json_files:
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        metrics = data.get('metrics', {})
        if 'ml_regime_label' not in metrics:
            ticker = data.get('ticker', json_file.name)
            print(f"❌ {ticker}: Missing ml_regime_label")
            print(f"   Available metrics: {list(metrics.keys())}")
    except Exception as e:
        print(f"Error reading {json_file.name}: {e}")
