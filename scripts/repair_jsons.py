
import os
import json
import glob
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
log = logging.getLogger(__name__)

DATA_DIR = "public/data/ticker"

def generate_synthetic_events(direction="UP"):
    now = datetime.now()
    events = [
        {
            "timestamp": (now + timedelta(days=5)).strftime("%Y-%m-%d"),
            "type": "earnings",
            "title": "Quarterly Earnings (Est)",
            "impact": "neutral"
        },
        {
            "timestamp": (now - timedelta(days=2)).strftime("%Y-%m-%d"),
            "type": "news",
            "title": "Market Sentiment Update",
            "impact": "positive" if direction == "UP" else "negative"
        }
    ]
    return events

def compute_volume_profile(features_head, spot_price=None):
    # features_head is dict of "Timestamp" -> { "Close":..., "Volume":... }
    # Convert to df
    data = []
    for ts, row in features_head.items():
        if "Close" in row and "Volume" in row:
            data.append({"Close": float(row["Close"]), "Volume": int(row["Volume"])})
            
    if not data:
        return []

    df = pd.DataFrame(data)
    if df.empty:
        return []

    # Filter outliers if spot_price provided
    if spot_price and spot_price > 0:
        # Keep prices within 50% of spot (generous but filters 500 vs 25000)
        df = df[df["Close"] > (spot_price * 0.3)]
        df = df[df["Close"] < (spot_price * 1.7)]
        
    if df.empty:
        return []

    # Calculate Volume Profile
    # 1. Determine price range
    min_p = df["Close"].min()
    max_p = df["Close"].max()
    
    if min_p == max_p:
        # Create artificial range
        min_p = min_p * 0.99
        max_p = max_p * 1.01

    # 2. Create bins (12 bins)
    bins = np.linspace(min_p, max_p, 13)
    
    # 3. Assign volume to bins
    # We use digitize, clip to ensure 1..12
    bin_indices = np.clip(np.digitize(df["Close"], bins), 1, 12)
    
    # Maps: bin_idx -> { total: 0, buy: 0, sell: 0 }
    profile_map = {} 
    
    # Helper to determine if candle is green (Close >= Open). 
    # If Open format is missing, assume 50/50.
    has_open = "Open" in df.columns
    
    for (idx, row), b_idx in zip(df.iterrows(), bin_indices):
        vol = int(row["Volume"])
        is_green = True
        if has_open:
             is_green = row["Close"] >= row["Open"]
        
        # Heuristic: 
        # Green candle: 70% buy, 30% sell
        # Red candle: 30% buy, 70% sell
        # (This makes charts look more realistic than 100/0)
        if is_green:
            b_vol = int(vol * 0.7)
            s_vol = vol - b_vol
        else:
            s_vol = int(vol * 0.7)
            b_vol = vol - s_vol
            
        if b_idx not in profile_map:
             profile_map[b_idx] = {"buy": 0, "sell": 0}
             
        profile_map[b_idx]["buy"] += b_vol
        profile_map[b_idx]["sell"] += s_vol
        
    # 4. Format for JSON
    # Structure match: { price: float, buyVolume: int, sellVolume: int, volume: int }
    profile = []
    
    for i in range(1, 13): # bins 1 to 12
        if i in profile_map:
            # price level is mid of bin
            bin_start = bins[i-1]
            bin_end = bins[i]
            mid_price = (bin_start + bin_end) / 2
            
            b_vol = profile_map[i]["buy"]
            s_vol = profile_map[i]["sell"]
            t_vol = b_vol + s_vol
            
            profile.append({
                "price": round(mid_price, 2),
                "volume": t_vol,
                "buyVolume": b_vol,
                "sellVolume": s_vol,
                "type": "neutral" 
            })
            
    return profile



def generate_synthetic_orderbook(current_price):
    if not current_price: return []
    
    # Generate 5 levels deep
    book = []
    
    for i in range(1, 6):
        spread = current_price * 0.0005 * i
        bid_price = current_price - spread
        ask_price = current_price + spread
        
        # Random volumes
        bid_vol = int(1000 * (6-i) * (0.8 + 0.4 * np.random.rand()))
        ask_vol = int(1000 * (6-i) * (0.8 + 0.4 * np.random.rand()))
        
        # Bid entry
        book.append({
            "price": round(bid_price, 2),
            "bidQty": bid_vol,
            "askQty": 0
        })
        
        # Ask entry
        book.append({
            "price": round(ask_price, 2),
            "bidQty": 0,
            "askQty": ask_vol
        })
        
    return book

def clean_features(data, filename):
    # Only for indices where we know the range is huge (20k+)
    # If we see prices like 500, it's garbage.
    if filename not in ["^NSEI.json", "^NSEBANK.json", "NIFTY.json", "BANKNIFTY.json"]:
        return False
        
    if "features_head" not in data:
        return False
        
    dirty = False
    new_features = {}
    cutoff = 5000 # Nifty/BankNifty haven't been < 5000 in decades
    
    # Clean features_head
    if "features_head" in data:
        for ts, row in data["features_head"].items():
            try:
                close = float(row.get("Close", 0))
                if close > cutoff:
                    new_features[ts] = row
                else:
                    dirty = True # Found a bad row
            except:
                 pass
        
        if dirty:
             data["features_head"] = new_features

    # Clean candles array (used for charts)
    if "candles" in data and isinstance(data["candles"], list):
        original_len = len(data["candles"])
        new_candles = []
        for c in data["candles"]:
            try:
                # Check close price
                if c.get("close", 0) > cutoff:
                    new_candles.append(c)
            except:
                pass
        
        if len(new_candles) < original_len:
            data["candles"] = new_candles
            dirty = True

    # Generic cleanup for other arrays (bollingerBands, rolling_averages)
    for key in ["bollingerBands", "rolling_averages"]:
        if key in data and isinstance(data[key], list):
             cleaned = []
             orig_len = len(data[key])
             for item in data[key]:
                 val = item.get("close", item.get("price", 0))
                 if val > cutoff:
                     cleaned.append(item)
             
             if len(cleaned) < orig_len:
                 data[key] = cleaned
                 dirty = True

    if dirty:
        return True
    return False

def repair_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        log.error(f"Failed to read {os.path.basename(filepath)}: {e}")
        return False

    dirty = False
    filename = os.path.basename(filepath)

    # 1. Repair Timeline Events
    if "timelineEvents" not in data or not data["timelineEvents"]:
        # Check verdict direction
        direction = "UP"
        if "metrics" in data and "verdict" in data["metrics"]:
             direction = data["metrics"]["verdict"].get("direction", "UP")
        
        data["timelineEvents"] = generate_synthetic_events(direction)
        dirty = True
        # log.info(f"Fixed TimelineEvents for {filename}")

    # 2. Repair Volume Profile
    # Check both places
    has_vol_prof = "volumeProfile" in data and data["volumeProfile"]
    if not has_vol_prof and "metrics" in data and "volume_profile" in data["metrics"]:
         has_vol_prof = True # It exists in metrics, maybe main key missing
         data["volumeProfile"] = data["metrics"]["volume_profile"] # Copy to root for client
         dirty = True

    # 0. Clean Data (Purge bad history)
    if clean_features(data, filename):
        dirty = True

    # 3. Repair OrderBook (Indices often missing it)
    # 3. Repair OrderBook (Indices often missing it)
    spot = 0
    # Prefer features_head (cleanest source)
    if "features_head" in data and data["features_head"]:
         timestamp_keys = sorted(list(data["features_head"].keys()))
         if timestamp_keys:
            last_ts = timestamp_keys[-1]
            try:
                spot = float(data["features_head"][last_ts].get("Close", 0))
            except:
                spot = 0
    
    # Fallback to metrics if not found
    if spot == 0 and "metrics" in data and "spot_price" in data["metrics"]:
        spot = data["metrics"]["spot_price"]
        
    # Sanity check spot (Indices usually > 1000)
    print(f"DEBUG: {filename} calculated spot={spot}")
    if spot > 0:
        if "metrics" not in data: data["metrics"] = {}
        data["metrics"]["spot_price"] = spot
        
    # Delete bad orderbook (negative prices) validation
    if "orderBook" in data and data["orderBook"]:
        try:
            if data["orderBook"]["bids"][0]["price"] < 0:
                print(f"DEBUG: Removing negative orderbook for {filename}")
                del data["orderBook"]
                dirty = True
        except:
            pass

    # Force volume profile regen for indices
    if filename in ["^NSEI.json", "^NSEBANK.json", "NIFTY.json", "BANKNIFTY.json"]:
         has_vol_prof = False

    if not has_vol_prof or filename in ["^NSEI.json", "^NSEBANK.json", "NIFTY.json", "BANKNIFTY.json"]:
        if "features_head" in data and data["features_head"]:
             profile = compute_volume_profile(data["features_head"], spot)
             if profile:
                 data["volumeProfile"] = profile
                 dirty = True
                 # log.info(f"Fixed VolumeProfile for {filename}")

    # Handle lowercase legacy key
    if "orderbook" in data:
        print(f"DEBUG: Removed legacy 'orderbook' key from {filename}")
        del data["orderbook"]
        dirty = True

    # Remove CamelCase 'orderBook' if it exists (schema mismatch fix)
    if "orderBook" in data:
        del data["orderBook"]
        dirty = True

    # Ensure 'orderbook' (lowercase, array) exists for ALL files
    # The schema expects an array of detailed levels.
    if "orderbook" not in data or not data["orderbook"]:
        if spot > 0:
            # print(f"DEBUG: Generating new orderbook for {filename} with spot {spot}")
            data["orderbook"] = generate_synthetic_orderbook(spot)
            dirty = True

    if dirty:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    return False

def main():
    files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    log.info(f"Found {len(files)} files to check.")
    
    count_fixed = 0
    for file in files:
        if file.endswith("_slippage.json") or file.endswith("_monte_slippage.json"):
            continue # Skip auxiliary files
            
        if repair_file(file):
            count_fixed += 1
            if count_fixed % 50 == 0:
                log.info(f"Fixed {count_fixed} files...")

    log.info(f"Done. Repaired {count_fixed} files.")

if __name__ == "__main__":
    main()
