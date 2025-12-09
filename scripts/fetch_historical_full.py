
import os
import sys
import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from nselib import capital_market
import time

# Constants
START_DATE = "01-01-2005"  # NSE Format DD-MM-YYYY
START_DATE_YF = "2005-01-01" # YF Format YYYY-MM-DD
OUTPUT_DIR = r"c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx\public\data\raw"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Index Mapping
INDEX_MAP = {
    "NIFTY": {"nse_symbol": "NIFTY 50", "yf_symbol": "^NSEI"},
    "BANKNIFTY": {"nse_symbol": "NIFTY BANK", "yf_symbol": "^NSEBANK"}
}

def fetch_nse_data(symbol, is_index=False):
    """Fetch from NSE using nselib"""
    print(f"   [NSE] Fetching {symbol}...")
    try:
        if is_index:
            # Indices fetch
            df = capital_market.index_data(index=symbol, from_date=START_DATE, to_date=datetime.now().strftime("%d-%m-%Y"))
        else:
            # Stock fetch - Requires more care as nselib might limit range
            # For now, we use price_volume_and_delivery_position_data but it handles max 1 year usually?
            # Actually nselib handles internal chunking. Let's try.
            df = capital_market.price_volume_and_delivery_position_data(symbol=symbol, from_date=START_DATE, to_date=datetime.now().strftime("%d-%m-%Y"))
            
        if df is None or df.empty:
            print(f"   [NSE] No data returned for {symbol}")
            return None
            
        # Standardize Columns
        # NSE Index cols: OPEN_INDEX_VAL, HIGH_INDEX_VAL, CLOSE_INDEX_VAL, INDEX_DATE
        # NSE Stock cols: Date, OpenPrice, HighPrice, LowPrice, ClosePrice, TotalTradedQuantity
        
        df.columns = [c.strip() for c in df.columns]
        
        if is_index:
            rename_map = {
                'INDEX_DATE': 'Date',
                'OPEN_INDEX_VAL': 'Open',
                'HIGH_INDEX_VAL': 'High',
                'LOW_INDEX_VAL': 'Low',
                'CLOSE_INDEX_VAL': 'Close',
                'TRADED_QTY': 'Volume'
            }
        else:
            rename_map = {
                'Date': 'Date',
                'OpenPrice': 'Open',
                'HighPrice': 'High',
                'LowPrice': 'Low',
                'ClosePrice': 'Close',
                'TotalTradedQuantity': 'Volume'
            }
            
        # Filter only needed columns
        needed = list(rename_map.keys())
        # Check availability
        available = [c for c in needed if c in df.columns]
        df = df[available].rename(columns=rename_map)
        
        # Parse Dates
        try:
            df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
        except:
            df['Date'] = pd.to_datetime(df['Date'])
            
        df = df.set_index('Date').sort_index()
        
        # Cleanup numerics
        for col in ['Open', 'High', 'Low', 'Close']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # If Volume missing (some indices), fill 0
        if 'Volume' not in df.columns:
            df['Volume'] = 0
            
        return df
        
    except Exception as e:
        print(f"   [NSE] Error fetching {symbol}: {str(e)[:50]}...")
        return None

def fetch_yf_data(symbol):
    """Fetch from Yahoo Finance"""
    print(f"   [YF]  Fetching {symbol}...")
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=START_DATE_YF, auto_adjust=True)
        if df.empty:
            return None
            
        # YF returns Open, High, Low, Close, Volume
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Normalize Index (remove tz if present)
        df.index = df.index.tz_localize(None)
        return df
    except Exception as e:
        print(f"   [YF]  Error fetching {symbol}: {e}")
        return None

def merge_data(nse_df, yf_df):
    """Merge datasets prioritizing NSE"""
    if nse_df is None and yf_df is None:
        return None
    if nse_df is None:
        print("   [MERGE] Using only YF data")
        return yf_df
    if yf_df is None:
        print("   [MERGE] Using only NSE data")
        return nse_df
        
    # Merge
    # We want a union of dates.
    # If date exists in NSE, take NSE. Else take YF.
    
    print(f"   [MERGE] NSE: {len(nse_df)} rows, YF: {len(yf_df)} rows")
    
    # Combined index
    all_dates = nse_df.index.union(yf_df.index).unique().sort_values()
    merged = pd.DataFrame(index=all_dates)
    
    # Fill from NSE first
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        merged[col] = nse_df[col]
        # Fill gaps with YF
        merged[col] = merged[col].fillna(yf_df[col])
        
    return merged

def process_ticker(ticker_name, is_index=False):
    print(f"\nProcessing {ticker_name}...")
    
    
    nse_sym = ticker_name
    if ticker_name.endswith(".NS"):
        yf_sym = ticker_name
    else:
        yf_sym = f"{ticker_name}.NS"
    
    # Handle Indicies
    if ticker_name in INDEX_MAP:
        nse_sym = INDEX_MAP[ticker_name]["nse_symbol"]
        yf_sym = INDEX_MAP[ticker_name]["yf_symbol"]
        is_index = True
    elif ticker_name.startswith("^"):
        # If user passed ^NSEI directly
        if ticker_name == "^NSEI": 
            process_ticker("NIFTY", True)
            return
        if ticker_name == "^NSEBANK":
            process_ticker("BANKNIFTY", True)
            return
            
    # Remove .NS for NSE fetch if present in input
    if nse_sym.endswith(".NS"):
        nse_sym = nse_sym.replace(".NS", "")
        
    # 1. Fetch NSE
    nse_df = fetch_nse_data(nse_sym, is_index)
    
    # 2. Fetch YF
    yf_df = fetch_yf_data(yf_sym)
    
    # 3. Merge
    final_df = merge_data(nse_df, yf_df)
    
    if final_df is not None and not final_df.empty:
        # Save
        # If it's an index, we might want to save as NIFTY.csv AND NSEI.csv to cover all bases
        # But pipeline expects specific names.
        # User said "fetch csvs... then train".
        # Let's save as Friendly Name if possible.
        
        # Standardize name for file
        fname = ticker_name.replace(".NS", "")
        if ticker_name == "NIFTY": fname = "NSEI" # Map back for pipeline compatibility? Or keep friendly?
        # Actually pipeline checks INDEX_TICKER_MAP. 
        # If pipeline uses ^NSEI, it expects ^NSEI.csv or NSEI.csv?
        # Let's check pipeline. Pipeline uses `fetch_ohlcv` which uses `yf.download`.
        # If we want pipeline to use OUR csv, we need to modify pipeline to load local csv.
        # For now, let's save as BOTH friendly and yahoo symbol for indices.
        
        save_path = os.path.join(OUTPUT_DIR, f"{fname}.csv")
        final_df.to_csv(save_path)
        print(f"   [SAVE] Saved to {save_path} ({len(final_df)} rows)")
        
        # Validation
        last_price = final_df.iloc[-1]['Close']
        print(f"   [INFO] Last Date: {final_df.index[-1].date()}, Price: {last_price:.2f}")
        
        if is_index:
            # Also save as Yahoo Symbol for safety
            yf_save = INDEX_MAP[ticker_name]["yf_symbol"].replace("^", "") # e.g NSEI
            if yf_save != fname:
                path2 = os.path.join(OUTPUT_DIR, f"{yf_save}.csv")
                final_df.to_csv(path2)
                print(f"   [SAVE] Also saved copy to {path2}")

    else:
        print("   [ERROR] Failed to compile data.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tickers", nargs="+", help="List of tickers")
    parser.add_argument("--file", help="File with tickers")
    args = parser.parse_args()
    
    tickers = []
    if args.tickers:
        tickers.extend(args.tickers)
    if args.file:
        with open(args.file, 'r') as f:
            tickers.extend([l.strip() for l in f if l.strip()])
            
    if not tickers:
        print("No tickers provided.")
        return
        
    for t in tickers:
        try:
            process_ticker(t)
        except Exception as e:
            print(f"CRITICAL ERROR on {t}: {e}")

if __name__ == "__main__":
    main()
