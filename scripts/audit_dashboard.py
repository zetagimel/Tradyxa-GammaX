
import json
import os
import sys
import numpy as np

DATA_DIR = r"c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx\public\data\ticker"

def audit_file(filepath):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        issues = []
        filename = os.path.basename(filepath)
        
        # 1. Check Candles
        candles = data.get("candles", [])
        if len(candles) < 20:
            issues.append(f"Low candle count: {len(candles)}")
        else:
            # Check for Price Gaps (Corrupt Data)
            closes = [c.get("close", 0) for c in candles]
            if len(closes) > 0:
                current = closes[-1]
                avg_hist = np.mean(closes[:-5]) if len(closes) > 5 else current
                if current > 0 and avg_hist > 0:
                    ratio = current / avg_hist
                    if ratio > 5 or ratio < 0.2:
                        issues.append(f"Massive Price Gap: History Avg {avg_hist:.2f} vs Current {current:.2f}")

        # 2. Check Volume Profile
        vp = data.get("volumeProfile", [])
        if not vp:
            issues.append("Missing Volume Profile")
        elif len(vp) < 5:
            issues.append(f"Tiny Volume Profile: {len(vp)} buckets")

        # 3. Check Orderbook
        ob = data.get("orderbook", [])
        if not isinstance(ob, list):
            issues.append(f"Invalid Orderbook Type: {type(ob)}")
        elif not ob:
             # It's okay if missing for now, but good to know
             pass # issues.append("Missing Orderbook")
        else:
            # Check content
            if "price" not in ob[0]:
                 issues.append("Invalid Orderbook Schema (missing price)")

        # 4. Check Bollinger
        bb = data.get("bollingerBands", [])
        if len(bb) < 5:
            issues.append("Missing/Empty Bollinger Bands")

        return issues
        
    except Exception as e:
        return [f"Read Error: {str(e)}"]

def main():
    print("Starting Audit...")
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    
    report = {}
    
    for f in files:
        path = os.path.join(DATA_DIR, f)
        issues = audit_file(path)
        if issues:
            report[f] = issues
            
    # Print Summary
    print(f"\nAudit Complete. Scanned {len(files)} files.")
    print(f"Files with Issues: {len(report)}")
    
    print("\n--- Detailed Report (Top 20) ---")
    count = 0
    for f, errs in report.items():
        print(f"{f}: {', '.join(errs)}")
        count += 1
        if count >= 20:
             break
             
    # Specific Check for NIFTY/BANKNIFTY
    print("\n--- Index Check ---")
    for name in ["NIFTY.json", "BANKNIFTY.json"]:
        if name in report:
            print(f"{name}: {report[name]}")
        else:
            print(f"{name}: OK")

if __name__ == "__main__":
    main()
