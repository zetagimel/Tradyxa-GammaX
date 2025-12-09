"""
Generate realistic Volume Profile from OHLCV data
Volume Profile shows where most trading occurred at each price level
"""

import pandas as pd
import numpy as np
from typing import List, Dict

def generate_volume_profile_from_ohlcv(
    df_ohlcv: pd.DataFrame,
    price_buckets: int = 20,
    lookback_days: int = 60
) -> List[Dict]:
    """
    Generate Volume Profile from historical OHLCV data
    
    Args:
        df_ohlcv: DataFrame with Open, High, Low, Close, Volume columns
        price_buckets: Number of price levels to create
        lookback_days: How many days of history to use
        
    Returns:
        List of {price, volume, buyVolume, sellVolume} dicts
    """
    
    # Use last N days
    df = df_ohlcv.tail(lookback_days).copy()
    
    # Get price range from recent highs and lows
    min_price = df['Low'].min()
    max_price = df['High'].max()
    
    # Create price buckets
    price_levels = np.linspace(min_price, max_price, price_buckets)
    
    # Initialize volume at each price level
    volume_at_level = {level: 0 for level in price_levels}
    buy_volume_at_level = {level: 0 for level in price_levels}
    sell_volume_at_level = {level: 0 for level in price_levels}
    
    # Distribute volume across price levels
    # Higher volume when price was at High/Low (support/resistance)
    for idx, row in df.iterrows():
        high = row['High']
        low = row['Low']
        close = row['Close']
        volume = row['Volume']
        
        # Identify which price levels occurred in this candle
        candle_levels = [p for p in price_levels if low <= p <= high]
        
        if len(candle_levels) > 0:
            # Distribute volume evenly across levels in this candle
            vol_per_level = volume / len(candle_levels)
            
            for level in candle_levels:
                volume_at_level[level] += vol_per_level
                
                # Determine if this was buying or selling pressure
                # Close > Open = bullish = buying, Close < Open = bearish = selling
                if close > row['Open']:
                    # Bullish candle - more buying at higher prices
                    distance_from_top = (high - level) / (high - low) if high > low else 0
                    buy_ratio = 0.7 - distance_from_top * 0.2  # 50-70% buying
                else:
                    # Bearish candle - more selling at lower prices
                    distance_from_bottom = (level - low) / (high - low) if high > low else 0.5
                    buy_ratio = 0.3 + distance_from_bottom * 0.2  # 30-50% buying
                
                buy_vol = vol_per_level * buy_ratio
                sell_vol = vol_per_level * (1 - buy_ratio)
                
                buy_volume_at_level[level] += buy_vol
                sell_volume_at_level[level] += sell_vol
    
    # Build result
    result = []
    for level in sorted(price_levels):
        result.append({
            'price': round(level, 2),
            'volume': int(volume_at_level[level]),
            'buyVolume': int(buy_volume_at_level[level]),
            'sellVolume': int(sell_volume_at_level[level])
        })
    
    return result


# Test it
if __name__ == "__main__":
    # Load real OHLCV data
    df = pd.read_csv("public/data/raw/RELIANCE_NS.csv", index_col=0, parse_dates=True)
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    vp = generate_volume_profile_from_ohlcv(df, price_buckets=15, lookback_days=60)
    
    print("Volume Profile from Real Data:")
    print("Price\t\tVolume\t\tBuy\t\tSell")
    print("-" * 60)
    for bucket in vp:
        print(f"₹{bucket['price']:.2f}\t\t{bucket['volume']:,}\t\t{bucket['buyVolume']:,}\t\t{bucket['sellVolume']:,}")
