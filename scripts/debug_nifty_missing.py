
import json
import os

fp = "public/data/ticker/NIFTY.json"
fp_nse = "public/data/ticker/^NSEI.json"

for f in [fp, fp_nse]:
    if os.path.exists(f):
        try:
            with open(f, 'r') as file:
                data = json.load(file)
            print(f"--- {f} ---")
            print("Keys:", list(data.keys()))
            feat = data.get("features_head", {})
            print(f"features_head len: {len(feat)}")
            if len(feat) < 5:
                print("features_head:", feat)
            candles = data.get("candles", [])
            print(f"candles len: {len(candles)}")
            if "volumeProfile" in data:
                print("volumeProfile: FOUND, len=", len(data["volumeProfile"]))
            else:
                print("volumeProfile: MISSING")
            
            if "orderbook" in data:
                 print("orderbook: FOUND")
            else:
                 print("orderbook: MISSING")
                 
        except Exception as e:
            print(f"Error reading {f}: {e}")
    else:
        print(f"File not found: {f}")
