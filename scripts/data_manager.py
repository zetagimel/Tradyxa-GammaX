import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import logging
import warnings

# Suppress yfinance FutureWarning (not our code)
warnings.filterwarnings('ignore', category=FutureWarning, module='yfinance')

# Configure logging - reduce verbosity
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = os.path.join("public", "data", "raw")
os.makedirs(DATA_DIR, exist_ok=True)

def get_csv_path(ticker: str) -> str:
    # Sanitize ticker for filename
    safe_ticker = ticker.replace("^", "").replace(".", "_")
    return os.path.join(DATA_DIR, f"{safe_ticker}.csv")

def load_data(ticker: str) -> pd.DataFrame:
    """Load data from local CSV if exists, else return empty DataFrame."""
    csv_path = get_csv_path(ticker)
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, index_col=0)
            # Ensure index is DatetimeIndex
            df.index = pd.to_datetime(df.index)
            return df
        except Exception as e:
            logger.error(f"Error reading CSV for {ticker}: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def save_data(ticker: str, df: pd.DataFrame):
    """Save DataFrame to local CSV."""
    csv_path = get_csv_path(ticker)
    df.to_csv(csv_path)
    logger.info(f"Saved data for {ticker} to {csv_path}")

def fetch_and_update_data(ticker: str, period: str = "10y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch data for ticker.
    1. If CSV exists:
       - Update forward (append new days).
       - Backfill backward (if data starts after 2005-01-01).
    2. If CSV doesn't exist:
       - Fetch full history from 2005-01-01.
    """
    csv_path = get_csv_path(ticker)
    existing_df = load_data(ticker)
    
    # Target start date: 2005-01-01
    TARGET_START = datetime(2005, 1, 1)
    
    # Defensive: Deduplicate existing data immediately
    if not existing_df.empty:
        # Fix for "Open.1", "Close.1" corrupted columns from previous bad runs
        # Keep only the standard columns
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        valid_cols = [c for c in existing_df.columns if c in required_cols]
        existing_df = existing_df[valid_cols]
        
        existing_df = existing_df[~existing_df.index.duplicated(keep='last')]
        # Ensure unique columns
        existing_df = existing_df.loc[:, ~existing_df.columns.duplicated()]
    
    if not existing_df.empty:
        # --- 1. Forward Update ---
        last_date = existing_df.index[-1]
        # Ensure last_date is timezone-naive
        if hasattr(last_date, 'tzinfo') and last_date.tzinfo is not None:
            last_date = last_date.tz_convert(None)
            
        start_date = last_date + timedelta(days=1)
        
        # Only fetch if there is a gap
        if start_date < datetime.now() - timedelta(hours=12): # Simple check to avoid fetching if run same day
            logger.info(f"Fetching update for {ticker} from {start_date.date()}")
            try:
                new_df = yf.download(ticker, start=start_date, interval=interval, progress=False, threads=False, auto_adjust=True)
                if not new_df.empty:
                    # Clean and standardize
                    new_df = _clean_yfinance_df(new_df)
                    
                    if not new_df.empty:
                        # Combine and deduplicate
                        existing_df = pd.concat([existing_df, new_df])
                        existing_df = existing_df[~existing_df.index.duplicated(keep='last')]
                        existing_df = existing_df.sort_index()
                        save_data(ticker, existing_df)
            except Exception as e:
                logger.error(f"Failed to update {ticker}: {e}")

        # --- 2. Backward Backfill ---
        first_date = existing_df.index[0]
        if hasattr(first_date, 'tzinfo') and first_date.tzinfo is not None:
            first_date = first_date.tz_convert(None)
            
        # If existing data starts significantly after 2005, try to backfill
        if first_date > TARGET_START + timedelta(days=10):
            logger.info(f"Attempting backfill for {ticker} (Current start: {first_date.date()}, Target: 2005)")
            try:
                # Fetch from 2005 up to the current first date
                # yfinance 'end' is exclusive, so this fetches up to first_date-1
                backfill_df = yf.download(ticker, start=TARGET_START, end=first_date, interval=interval, progress=False, threads=False, auto_adjust=True)
                
                if not backfill_df.empty:
                    backfill_df = _clean_yfinance_df(backfill_df)
                    
                    if not backfill_df.empty:
                        # Defensive: Deduplicate backfill data
                        backfill_df = backfill_df[~backfill_df.index.duplicated(keep='last')]
                        
                        logger.info(f"Found {len(backfill_df)} older rows for {ticker}")
                        
                        # Concatenate
                        existing_df = pd.concat([backfill_df, existing_df])
                        
                        # Final cleanup
                        existing_df = existing_df[~existing_df.index.duplicated(keep='last')]
                        existing_df = existing_df.sort_index()
                        save_data(ticker, existing_df)
            except Exception as e:
                # Just log warning and continue with existing data
                logger.warning(f"Backfill skipped for {ticker}: {e}")

        return existing_df
    
    # --- 3. Full Fetch (New File) ---
    logger.info(f"Fetching full history (from 2005) for {ticker}")
    try:
        df = yf.download(ticker, start=TARGET_START, interval=interval, progress=False, threads=False, auto_adjust=True)
        if df.empty:
             raise ValueError("Empty data returned for specific start date")
             
        df = _clean_yfinance_df(df)
        if not df.empty:
            save_data(ticker, df)
            return df
            
    except Exception as e:
        logger.warning(f"Could not fetch from 2005 for {ticker} ({e}). Falling back to period='max'...")
        try:
            # Fallback: Fetch max available history
            df = yf.download(ticker, period="max", interval=interval, progress=False, threads=False, auto_adjust=True)
            if not df.empty:
                df = _clean_yfinance_df(df)
                if not df.empty:
                    save_data(ticker, df)
                    return df
        except Exception as e2:
            logger.error(f"Failed to fetch initial data for {ticker}: {e2}")
    
    return existing_df

def _clean_yfinance_df(df: pd.DataFrame) -> pd.DataFrame:
    """Helper to clean and standardize yfinance DataFrame"""
    # Handle MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        try:
            if 'Close' in df.columns.get_level_values(0):
                df.columns = df.columns.get_level_values(0)
            elif 'Close' in df.columns.get_level_values(1):
                df.columns = df.columns.get_level_values(1)
        except Exception:
            pass

    # Standardize columns
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    
    # Defensive: Drop duplicate columns immediately
    if df.columns.duplicated().any():
        logger.warning(f"Duplicate columns detected: {df.columns[df.columns.duplicated()]}")
        df = df.loc[:, ~df.columns.duplicated()]
        logger.warning(f"Columns after deduplication: {df.columns}")
    
    available_cols = [c for c in required_cols if c in df.columns]
    
    if len(available_cols) < 5:
        return pd.DataFrame()

    df = df[available_cols]
    if df.index.tz is not None:
        df.index = df.index.tz_convert(None)
    
    # Defensive: Drop rows where Close is NaN (empty trading days)
    df = df.dropna(subset=['Close'])
    
    return df

if __name__ == "__main__":
    # Test with NIFTY
    fetch_and_update_data("^NSEI")
