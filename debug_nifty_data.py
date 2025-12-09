import yfinance as yf
import pandas as pd

def debug_nifty():
    ticker = "^NSEI"
    print(f"Fetching {ticker} from 2005-01-01...")
    
    # Use the same parameters as data_manager
    df = yf.download(ticker, start="2005-01-01", progress=False, threads=False, auto_adjust=True)
    
    print(f"Raw Shape: {df.shape}")
    print("First 5 rows:")
    print(df.head())
    
    print("\nChecking for NaNs:")
    print(df.isna().sum())
    
    # Check specific dates user mentioned
    print("\nChecking 2007-09-17:")
    try:
        print(df.loc["2007-09-17"])
    except KeyError:
        print("Date 2007-09-17 not in index")

    # Check recent date
    print("\nChecking recent dates (tail):")
    print(df.tail())

if __name__ == "__main__":
    debug_nifty()
