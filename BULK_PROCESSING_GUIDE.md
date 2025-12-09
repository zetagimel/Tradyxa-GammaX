# 🚀 Bulk Processing Guide - Tradyxa Aztryx

Complete guide to process all 500+ stocks and generate dashboard data.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start Commands](#quick-start-commands)
3. [Detailed Step-by-Step](#detailed-step-by-step)
4. [Expected Output](#expected-output)
5. [Timeline](#timeline)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. Install Python Dependencies

From the root directory:

```bash
cd c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx
pip install -r requirements.txt
```

**Dependencies installed:**
- pandas >= 2.0.0
- numpy >= 1.24.0
- yfinance >= 0.2.30
- scikit-learn >= 1.3.0
- joblib >= 1.3.0
- requests >= 2.31.0

---

## 🎯 Quick Start Commands

**Copy and paste this entire block:**

```bash
# Navigate to project root
cd c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx

# Step 1: Fetch ticker list (10 seconds)
python scripts/fetch_tickers.py

# Step 2: Generate data for all 503 stocks (30-60 minutes)
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf

# Step 3: Train ML models (2-5 minutes)
python scripts/train_regime_classifier.py
python scripts/train_slippage_quantile.py

# Step 4: Apply ML predictions (30 seconds)
python scripts/apply_models.py

# Step 5: Fetch live spot prices (30 seconds)
python scripts/fetch_spot_prices.py

# Done! Start the dashboard
npm run dev
```

---

## 📖 Detailed Step-by-Step

### Step 1: Fetch Ticker List

```bash
python scripts/fetch_tickers.py
```

**What it does:**
- Downloads NIFTY 500 constituent list from NSE
- Adds NIFTY 50 (`^NSEI`) and BANKNIFTY (`^NSEBANK`) indices
- Saves all 503 tickers to `scripts/nifty500.txt`

**Output:**
```
scripts/nifty500.txt (503 ticker symbols)
```

**Time:** ~10 seconds

---

### Step 2: Generate Data for All Stocks (BULK PROCESSING)

```bash
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
```

**What it does:**
- Fetches 5 years of OHLCV data for all 503 stocks
- Computes features (Amihud, Lambda, MFC, volatility, etc.)
- Runs slippage simulations (deterministic + Monte Carlo)
- Generates verdict (UP/DOWN with confidence)
- Creates data for all 13 dashboard tiles

**Parameters:**
- `--mode batch_run` - Process multiple tickers
- `--tickers-file scripts/nifty500.txt` - Input file with tickers
- `--max-workers 4` - Parallel processing (4 stocks at once)
- `--use-yf` - Use yfinance for data fetching

**Adjust workers based on your PC:**
- Fast PC: `--max-workers 8`
- Slow PC: `--max-workers 2`

**Output:**
```
public/data/raw/<TICKER>.csv          - OHLCV data for each stock
public/data/ticker/<TICKER>.json      - Features + metrics + verdict
public/data/ticker/<TICKER>_slippage.json - Slippage stats
public/data/ticker/<TICKER>_monte_slippage.json - Monte Carlo results
```

**Time:** 30-60 minutes (depends on internet speed and CPU)

**Progress indicator:**
```
Processing: RELIANCE.NS (1/503)
Processing: TCS.NS (2/503)
Processing: HDFCBANK.NS (3/503)
...
```

---

### Step 3: Train ML Models

#### 3a. Train Regime Classifier

```bash
python scripts/train_regime_classifier.py
```

**What it does:**
- Loads data from ALL 503 ticker JSON files
- Combines ~230k feature rows
- Labels based on slippage severity:
  - 0 = LOW (p90 slippage < 3%)
  - 1 = NORMAL (3% - 7%)
  - 2 = HIGH (7% - 15%)
  - 3 = SEVERE (> 15%)
- Trains RandomForest classifier

**Output:**
```
models/rf_execution_regime.joblib
models/rf_execution_regime_metadata.json
```

**Time:** 2-3 minutes

---

#### 3b. Train Slippage Forecasting Models

```bash
python scripts/train_slippage_quantile.py
```

**What it does:**
- Loads data from ALL 503 ticker JSON files
- Trains two GradientBoosting models:
  - Q50 (median slippage predictor)
  - Q90 (tail risk / worst-case predictor)

**Output:**
```
models/qr_slippage_q50.joblib
models/qr_slippage_q90.joblib
```

**Time:** 2-3 minutes

---

### Step 4: Apply ML Predictions

```bash
python scripts/apply_models.py
```

**What it does:**
- Loads the 3 trained models
- Reads each ticker's JSON file
- Extracts latest feature row
- Makes predictions:
  - Regime classification (0-3)
  - Median slippage forecast
  - P90 slippage forecast
- Updates each JSON with ML predictions

**Updates:**
- All `public/data/ticker/*.json` files with predictions
- Enhances Tile 3 (Slippage Expectation)
- Enhances Tile 13 (Verdict)

**Time:** ~30 seconds

---

### Step 5: Fetch Live Spot Prices

```bash
python scripts/fetch_spot_prices.py
```

**What it does:**
- Fetches current spot price for all 503 stocks
- Fetches India VIX (volatility index)
- Saves to a single lightweight JSON (~50 KB)

**Output:**
```
public/data/live/spot_prices.json
```

**Time:** ~30 seconds

---

## 📊 Expected Output

After completing all steps, you should have:

### CSV Files (503 files)
```
public/data/raw/
├── ^NSEI.csv
├── ^NSEBANK.csv
├── RELIANCE.NS.csv
├── TCS.NS.csv
└── ... (500+ more)
```

### JSON Files (503 × 3 = 1509 files)
```
public/data/ticker/
├── ^NSEI.json
├── ^NSEI_slippage.json
├── ^NSEI_monte_slippage.json
├── RELIANCE.NS.json
├── RELIANCE.NS_slippage.json
├── RELIANCE.NS_monte_slippage.json
└── ... (1500+ more)
```

### ML Models (3 files)
```
models/
├── rf_execution_regime.joblib
├── qr_slippage_q50.joblib
└── qr_slippage_q90.joblib
```

### Live Prices (1 file)
```
public/data/live/
└── spot_prices.json
```

---

## ⏱️ Timeline

| Step | Time | Description |
|------|------|-------------|
| **Step 1** | 10 seconds | Fetch ticker list |
| **Step 2** | **30-60 minutes** | Generate all 503 stocks |
| **Step 3a** | 2-3 minutes | Train regime classifier |
| **Step 3b** | 2-3 minutes | Train slippage models |
| **Step 4** | 30 seconds | Apply predictions |
| **Step 5** | 30 seconds | Fetch live prices |
| **TOTAL** | **~35-70 minutes** | Complete setup |

---

## 🔧 Troubleshooting

### Error: "Can't open file"

**Problem:** Running command from wrong directory

**Solution:**
```bash
# Always run from root directory
cd c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
```

---

### Error: "No module named 'pandas'"

**Problem:** Dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt
```

---

### Error: "Connection refused" or "Rate limit"

**Problem:** yfinance API rate limits

**Solution:**
- Wait 5 minutes and try again
- Reduce `--max-workers` to 2
- Run in smaller batches:
  ```bash
  # Create smaller ticker files
  head -n 100 scripts/nifty500.txt > scripts/batch1.txt
  python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/batch1.txt --max-workers 2 --use-yf
  ```

---

### Slow Processing

**Problem:** Taking too long

**Solutions:**
1. **Increase workers** (if you have a fast PC):
   ```bash
   python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 8 --use-yf
   ```

2. **Check internet speed** - yfinance downloads ~500 MB of data

3. **Run overnight** - Let it complete without interruption

---

### Out of Memory

**Problem:** Script crashes due to memory

**Solution:**
- Reduce `--max-workers` to 2
- Close other applications
- Process in smaller batches (100 stocks at a time)

---

## 🔄 Ongoing Maintenance

### Daily Updates (Incremental)

```bash
# Only fetches new data since last run (much faster!)
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 2 --use-yf
python scripts/apply_models.py
python scripts/fetch_spot_prices.py
```

**Time:** ~10-15 minutes

---

### Weekly Model Training

```bash
# Retrain models on all accumulated data
python scripts/train_regime_classifier.py
python scripts/train_slippage_quantile.py
python scripts/apply_models.py
```

**Time:** ~5 minutes

---

## 🎯 Quick Reference

### Process a Single Stock
```bash
python scripts/tradyxa_pipeline.py --mode run_all --ticker RELIANCE.NS --use-yf
```

### Process Specific Stocks
```bash
# Create custom ticker file
echo ^NSEI > scripts/my_tickers.txt
echo RELIANCE.NS >> scripts/my_tickers.txt
echo TCS.NS >> scripts/my_tickers.txt

# Process
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/my_tickers.txt --max-workers 2 --use-yf
```

### Check What Data Exists
```bash
# Count CSV files
ls public/data/raw/*.csv | Measure-Object

# Count JSON files
ls public/data/ticker/*.json | Measure-Object

# Check models
ls models/*.joblib
```

---

## 📚 Additional Documentation

- [README.md](README.md) - Main project documentation
- [MODEL_TRAINING_AND_DATA_DEPENDENCIES.md](MODEL_TRAINING_AND_DATA_DEPENDENCIES.md) - ML model details
- [DATA_FETCHING_ARCHITECTURE.md](DATA_FETCHING_ARCHITECTURE.md) - Data pipeline architecture
- [scripts/README.md](scripts/README.md) - Python scripts reference

---

## ✅ Verification

After running all steps, verify:

1. **Check CSV count:**
   ```bash
   ls public/data/raw/*.csv | Measure-Object
   ```
   Should show **503 files**

2. **Check JSON count:**
   ```bash
   ls public/data/ticker/*.json | Measure-Object
   ```
   Should show **~1509 files** (503 × 3)

3. **Check models:**
   ```bash
   ls models/*.joblib
   ```
   Should show **3 files**

4. **Start dashboard:**
   ```bash
   npm run dev
   ```
   Open http://localhost:5173 and check if data loads

---

## 🚀 Ready to Start?

Run this now:

```bash
cd c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
```

**Estimated time:** 30-60 minutes for all 503 stocks

Good luck! 🎯
