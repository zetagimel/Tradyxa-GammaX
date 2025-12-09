#!/usr/bin/env python3
"""
update_spot_from_csv.py

Updates metrics.spot_price in all JSON files using the latest Close price from corresponding CSVs.
This ensures the dashboard shows the most recent closing price when live data is unavailable.
"""

import os
import json
import glob
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
log = logging.getLogger(__name__)

JSON_DIR = "public/data/ticker"
CSV_DIR = "public/data/raw"

# Mapping from JSON filename to CSV filename
def get_csv_for_json(json_filename):
    """Map JSON filename to corresponding CSV."""
    base = json_filename.replace('.json', '')
    
    # Handle index naming
    if base == 'NIFTY' or base == '^NSEI':
        return 'NSEI.csv'
    elif base == 'BANKNIFTY' or base == '^NSEBANK':
        return 'NSEBANK.csv'
    elif base.endswith('.NS'):
        # RELIANCE.NS.json -> RELIANCE.csv
        return base.replace('.NS', '') + '.csv'
    else:
        # Try with and without .NS
        return base + '.csv'

def get_latest_close(csv_path):
    """Read CSV and return latest Close price."""
    try:
        df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        if df.empty:
            return None
        
        # Get the last row's Close price
        last_close = df['Close'].iloc[-1]
        return float(last_close)
    except Exception as e:
        log.warning(f"Failed to read {csv_path}: {e}")
        return None

def update_json_spot_price(json_path, new_spot):
    """Update metrics.spot_price in JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'metrics' not in data:
            data['metrics'] = {}
        
        old_spot = data['metrics'].get('spot_price', 0)
        
        # Only update if significantly different (avoid rounding noise)
        if abs(new_spot - old_spot) > 0.01:
            data['metrics']['spot_price'] = new_spot
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return True
        return False
    except Exception as e:
        log.error(f"Failed to update {json_path}: {e}")
        return False

def main():
    log.info("Updating spot prices from CSVs...")
    
    json_files = glob.glob(os.path.join(JSON_DIR, "*.json"))
    updated = 0
    skipped = 0
    
    for json_path in json_files:
        filename = os.path.basename(json_path)
        
        # Skip auxiliary files
        if '_slippage' in filename or '_monte' in filename:
            continue
        
        csv_filename = get_csv_for_json(filename)
        csv_path = os.path.join(CSV_DIR, csv_filename)
        
        if not os.path.exists(csv_path):
            # Try alternate naming
            alt_csv = csv_filename.replace('.csv', '.NS.csv')
            alt_path = os.path.join(CSV_DIR, alt_csv)
            if os.path.exists(alt_path):
                csv_path = alt_path
            else:
                skipped += 1
                continue
        
        latest_close = get_latest_close(csv_path)
        if latest_close and latest_close > 0:
            if update_json_spot_price(json_path, latest_close):
                updated += 1
                if updated <= 5 or updated % 100 == 0:
                    log.info(f"Updated {filename}: spot_price = {latest_close:.2f}")
    
    log.info(f"Done. Updated {updated} files, skipped {skipped} (no CSV found).")

if __name__ == "__main__":
    main()
