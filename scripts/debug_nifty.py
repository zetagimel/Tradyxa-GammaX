
import json
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

def compute_volume_profile(features_head):
    # features_head is dict of "Timestamp" -> { "Close":..., "Volume":... }
    # Convert to df
    data = []
    for ts, row in features_head.items():
        if "Close" in row and "Volume" in row:
            try:
                data.append({"Close": float(row["Close"]), "Volume": int(row["Volume"])})
            except ValueError:
                continue
            
    if not data:
        print("Data extraction failed: No valid rows")
        return []

    df = pd.DataFrame(data)
    print(f"Extracted {len(df)} rows.")
    print(df.head())
    
    if df.empty:
        print("DataFrame empty")
        return []

    # Calculate Volume Profile
    # 1. Determine price range
    min_p = df["Close"].min()
    max_p = df["Close"].max()
    print(f"Min: {min_p}, Max: {max_p}")
    
    if min_p == max_p:
        print("Min price equals Max price")
        return []

    # 2. Create bins (12 bins)
    bins = np.linspace(min_p, max_p, 13)
    
    # 3. Assign volume to bins
    # We use digitize
    bin_indices = np.digitize(df["Close"], bins)
    
    profile_map = {} # bin_idx -> volume sum
    
    for i, row in df.iterrows():
        b_idx = bin_indices[i]
        vol = row["Volume"]
        profile_map[b_idx] = profile_map.get(b_idx, 0) + vol
        
    # 4. Format for JSON
    # Structure: { price: float, volume: int, type: "neutral" }
    profile = []
    total_vol = df["Volume"].sum()
    print(f"Total Volume: {total_vol}")
    
    for i in range(1, 13): # bins 1 to 12
        if i in profile_map:
            # price level is mid of bin
            bin_start = bins[i-1]
            bin_end = bins[i]
            mid_price = (bin_start + bin_end) / 2
            vol = int(profile_map[i])
            
            # Simple POC detection (Point of Control - Max Volume)
            # Not strict, just valid structure
            profile.append({
                "price": round(mid_price, 2),
                "volume": vol,
                "type": "neutral" 
            })
            
    return profile

with open("public/data/ticker/NIFTY.json", "r") as f:
    d = json.load(f)
    print("Loaded NIFTY.json")
    if "features_head" in d:
        print("Found features_head")
        p = compute_volume_profile(d["features_head"])
        print(f"Profile: {p}")
    else:
        print("features_head missing")
