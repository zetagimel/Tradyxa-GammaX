# Incident Report: Index Data & Orderbook Fixes (2025-12-08)

## 1. Problem Description
-   **Index Charts Broken**: NIFTY/BANKNIFTY charts (Bollinger, Volume Profile) were flat/spiked due to corrupted historical data (prices ~500 mixed with ~26,000).
-   **Orderbook Disappeared**: After an initial repair attempt, the "Orderbook Depth" tile went blank for all 500+ stocks.
    -   **Cause**: The repair script deleted the legacy `orderbook` (lowercase) key and generated a new `orderBook` (CamelCase) key.
    -   **Complication**: The new `orderBook` format (Object `{bids, asks}`) mismatched the frontend schema (Array `[{price, qty}]`), causing the tile to fail to render even if the key matched.

## 2. Root Cause Analysis
-   **Data Quality**: `yfinance` history for indices contained ancient/outlier data points.
-   **Schema Mismatch**: The Python backend generated an Object, while the React frontend expected an Array.
-   **Incomplete Migration**: The frontend code strictly looked for `orderbook` (lowercase), so providing `orderBook` (CamelCase) was ignored.

## 3. Resolution
The `scripts/repair_jsons.py` script was updated to:
1.  **Purge Outliers**: Explicitly remove historical data points < 5000 for Indices from `features_head`, `candles`, `bollingerBands`, and `rolling_averages`.
2.  **Fix Schema**: Generate synthetic orderbooks as a **Flat Array** of objects (`{price, bidQty, askQty}`), satisfying the Zod schema.
3.  **Restore Key**: Write the data to the `orderbook` (lowercase) key, restoring compatibility with the existing frontend.
4.  **Batch Repair**: Executed the script across all 1518 JSON files to restore the missing orderbooks for all stocks.

## 4. Current Status
-   **Indices (NIFTY/BANKNIFTY)**: fully repaired. Charts zoom correctly. Volume Profile visible.
-   **All Stocks**: Orderbook Depth tile is populated and visible.
