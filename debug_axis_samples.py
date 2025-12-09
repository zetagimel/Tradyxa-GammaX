
import os
import sys
import pandas as pd
import logging

# Add scripts to path
sys.path.append(os.path.join(os.getcwd(), "scripts"))

import data_manager
import tradyxa_pipeline

# Setup logging
logging.basicConfig(level=logging.INFO)

def debug_axis():
    ticker = "AXISBANK"
    yf_ticker = "AXISBANK.NS"
    
    print(f"--- Debugging {ticker} ({yf_ticker}) ---")
    
    # 1. Check CSV directly
    csv_path = data_manager.get_csv_path(yf_ticker)
    print(f"CSV Path: {csv_path}")
    if os.path.exists(csv_path):
        df_csv = pd.read_csv(csv_path, index_col=0)
        print(f"CSV Rows: {len(df_csv)}")
        print(f"CSV Start: {df_csv.index[0]}")
        print(f"CSV End: {df_csv.index[-1]}")
    else:
        print("CSV does not exist!")
        return

    # 2. Check fetch_ohlcv
    print("\n--- Calling fetch_ohlcv ---")
    df_ohlcv = tradyxa_pipeline.fetch_ohlcv(ticker)
    if df_ohlcv is not None:
        print(f"fetch_ohlcv Rows: {len(df_ohlcv)}")
    else:
        print("fetch_ohlcv returned None")
        return

    # 3. Check compute_features_for_df
    print("\n--- Calling compute_features_for_df ---")
    df_features = tradyxa_pipeline.compute_features_for_df(df_ohlcv)
    print(f"df_features Rows: {len(df_features)}")

    # 4. Check slippage simulation
    print("\n--- Calling deterministic_slippage_simulation ---")
    slip_res = tradyxa_pipeline.deterministic_slippage_simulation(df_features, 100000)
    print(f"Slippage Samples: {len(slip_res['sample'])}")

    # 5. Check JSON
    json_path = os.path.join("public", "data", "ticker", f"{ticker}.json")
    if os.path.exists(json_path):
        import json
        with open(json_path, 'r') as f:
            data = json.load(f)
        print(f"\nJSON n_samples: {data['metrics']['verdict']['n_samples']}")
    else:
        print("JSON not found")

if __name__ == "__main__":
    debug_axis()
