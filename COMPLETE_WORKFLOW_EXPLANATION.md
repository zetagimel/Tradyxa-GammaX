# Complete Workflow Explanation - CSV → ML → JSON → Dashboard

## 📋 Overview

This document explains the **complete automated workflow** from fetching CSV data to displaying computed tiles in the dashboard.

---

## 🔄 Complete Data Flow

```
1. CSV Fetching (yfinance from 2005)
   ↓
2. ML Training (Weekly - Sunday)
   ↓
3. Daily CSV Update (Append new day)
   ↓
4. JSON Generation (All computed tiles)
   ↓
5. Friendly Name Copies (NIFTY.json, BANKNIFTY.json)
   ↓
6. ML Predictions Applied
   ↓
7. Live Prices Overlay
   ↓
8. GitHub Commit & Deploy
   ↓
9. Dashboard Displays All Tiles
```

---

## 🎯 GitHub Actions Workflows

### **1. Initial Setup** (Run Once Manually)
**File:** `.github/workflows/initial-setup.yml`

**What it does:**
1. ✅ Fetches all 503 CSVs from 2005 to today
2. ✅ Generates JSON files with all computed tiles
3. ✅ Creates friendly name copies (NIFTY.json, BANKNIFTY.json)
4. ✅ Trains ML models (regime classifier + slippage forecasters)
5. ✅ Applies ML predictions to all JSONs
6. ✅ Fetches live spot prices
7. ✅ Commits everything to GitHub

**Output:**
- `public/data/raw/*.csv` (503 CSV files)
- `public/data/ticker/*.json` (503 JSON files with computed data)
- `public/data/ticker/NIFTY.json` & `BANKNIFTY.json` (friendly copies)
- `models/*.joblib` (trained ML models)
- `public/data/live/spot_prices.json` (live prices)

---

### **2. Daily Update** (Mon-Fri 3:45 PM IST)
**File:** `.github/workflows/daily_update.yml`

**What it does:**
1. ✅ **Incremental CSV Update**: Fetches only NEW data since last update
   - Uses `data_manager.py` to check last date in CSV
   - Only downloads missing days (usually just 1 day)
   - Appends to existing CSV files

2. ✅ **JSON Generation**: Runs `tradyxa_pipeline.py`
   - Reads updated CSV
   - Computes all features (Amihud, Lambda, MFC, etc.)
   - Generates ALL 12 tile data:
     - Volume Profile (20 buckets)
     - Orderbook Depth (20 levels)
     - Candles with Bollinger Bands (60 points)
     - Rolling Averages (60 points)
     - Absorption Flow (60 points)
     - Heatmap (45 cells)
     - Histogram (8 bins)
     - Slippage Samples (50 samples)
   - Calculates Verdict (UP/DOWN with confidence)
   - Saves as `^NSEI.json`, `^NSEBANK.json`, `STOCK.NS.json`

3. ✅ **Friendly Name Copies**: Creates `NIFTY.json` and `BANKNIFTY.json`
   - Copies `^NSEI.json` → `NIFTY.json` (updates meta.ticker)
   - Copies `^NSEBANK.json` → `BANKNIFTY.json` (updates meta.ticker)
   - Also copies slippage files

4. ✅ **ML Predictions**: Runs `apply_models.py`
   - Loads pre-trained models from `models/*.joblib`
   - Applies regime classification
   - Applies slippage forecasting (Q50, Q90)
   - Updates JSON files with ML predictions

5. ✅ **Live Prices**: Fetches current spot prices and VIX
   - Updates `public/data/live/spot_prices.json`
   - Includes India VIX (real-time)

6. ✅ **Commit & Deploy**: Pushes to GitHub
   - Cloudflare Pages auto-deploys
   - Dashboard shows updated data

**Output:**
- Updated CSVs (with new day appended)
- Updated JSONs (with all computed tiles)
- Updated live prices
- All committed to GitHub

---

### **3. Weekly Model Training** (Sunday 2:00 AM IST)
**File:** `.github/workflows/weekly-pipeline.yml`

**What it does:**
1. ✅ **Retrain ML Models**: Uses all existing CSV data
   - Trains regime classifier (RandomForest)
   - Trains slippage forecasters (Quantile Regression)
   - Saves new models to `models/*.joblib`

2. ✅ **Create Friendly Copies**: Ensures NIFTY.json and BANKNIFTY.json exist

3. ✅ **Apply Fresh Predictions**: Uses newly trained models
   - Updates all JSON files with latest ML predictions

4. ✅ **Commit Models**: Pushes trained models to GitHub

**Output:**
- Retrained ML models
- Updated JSONs with fresh predictions

---

### **4. Live Spot Prices** (Every 2 Hours During Market Hours)
**File:** `.github/workflows/live_spot_prices.yml`

**What it does:**
1. ✅ Fetches current spot prices for all 500+ stocks
2. ✅ Fetches India VIX
3. ✅ Updates `public/data/live/spot_prices.json`
4. ✅ Commits and deploys

**Output:**
- Updated `spot_prices.json` with real-time data

---

## 📊 What Gets Computed in JSON Files

### **From CSV Data (No ML Required):**
1. **Volume Profile** - Price level distribution (20 buckets)
2. **Orderbook Depth** - Synthetic bid/ask levels (20 levels)
3. **Candles with Bollinger Bands** - OHLC + bands (60 points)
4. **Rolling Averages** - MA5, MA20, MA50 (60 points)
5. **Absorption Flow** - Buy/sell flow analysis (60 points)
6. **Heatmap** - Activity by hour/day (45 cells)
7. **Histogram** - Returns distribution (8 bins)
8. **Slippage Samples** - Historical slippage data (50 samples)

### **With ML Enhancement:**
9. **Slippage Expectation** - Enhanced with Q50/Q90 predictions
10. **Verdict** - Enhanced with regime classifier + slippage predictions

### **Live Data Overlay:**
11. **Spot Price** - Overlaid from `spot_prices.json`
12. **India VIX** - Overlaid from `spot_prices.json` (replaces hardcoded 15.0)

---

## 🔧 Pipeline Process (`tradyxa_pipeline.py`)

### **Step-by-Step:**

1. **Fetch OHLCV** (`data_manager.py`)
   - Checks CSV for last date
   - Fetches from yfinance (2005+ or incremental)
   - Saves to `public/data/raw/{TICKER}.csv`

2. **Feature Engineering**
   - Computes: Amihud, Lambda, MFC, Vol Z-Score, Coordinated Flow
   - Calculates: Volatility, Returns, HLC Ratio

3. **Slippage Simulation**
   - Deterministic slippage (volume-based)
   - Monte Carlo slippage (1000 simulations)
   - Saves to `{TICKER}_slippage.json` and `{TICKER}_monte_slippage.json`

4. **Verdict Calculation**
   - Combines: Momentum + Flow + Liquidity + Cost
   - Adds ML predictions (if available)
   - Generates UP/DOWN signal with confidence

5. **Tile Data Generation**
   - Volume Profile: 60-day lookback, 20 price buckets
   - Orderbook: Synthetic depth around current price
   - Bollinger Bands: 20-day window, 2 std dev
   - Rolling Averages: MA5, MA20, MA50
   - Absorption Flow: Buy/sell flow over time
   - Heatmap: Activity by hour/day
   - Histogram: Returns distribution
   - Slippage Samples: Historical slippage data

6. **Save JSON**
   - Saves as `{TICKER}.json` (e.g., `^NSEI.json`, `STOCK.NS.json`)
   - Contains: meta, metrics, features_head, and ALL computed tile data

7. **Create Friendly Copies** (for indices only)
   - `^NSEI.json` → `NIFTY.json` (updates meta.ticker)
   - `^NSEBANK.json` → `BANKNIFTY.json` (updates meta.ticker)

---

## ✅ Summary

**Yes, everything is automated in GitHub Actions:**

1. ✅ **CSV Fetching** - Automated (daily incremental, initial full)
2. ✅ **ML Training** - Automated (weekly on Sundays)
3. ✅ **Daily CSV Updates** - Automated (Mon-Fri 3:45 PM IST)
4. ✅ **JSON Generation** - Automated (with all computed tiles)
5. ✅ **Friendly Name Copies** - Automated (NIFTY.json, BANKNIFTY.json)
6. ✅ **ML Predictions** - Automated (applied after JSON generation)
7. ✅ **Live Prices** - Automated (every 2 hours)
8. ✅ **GitHub Commit** - Automated (all workflows commit)
9. ✅ **Cloudflare Deploy** - Automated (on every commit)

**The Dashboard automatically shows:**
- All computed tile data from JSON files
- Live spot prices (overlaid on JSON)
- Live VIX (overlaid on JSON, replaces hardcoded 15.0)
- ML-enhanced verdict and slippage

Everything runs automatically - no manual intervention needed! 🚀

