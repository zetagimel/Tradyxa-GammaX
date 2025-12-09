# 🎯 Quick Reference - Production Scripts to Run

## TL;DR - What to Deploy

### **3 GitHub Actions Workflows (Already Created)**

1. **`.github/workflows/live_spot_prices.yml`** → Every 30 min (market hours)
   ```bash
   python scripts/fetch_spot_prices.py
   # Output: public/data/live/spot_prices.json (real-time prices)
   ```

2. **`.github/workflows/daily_update.yml`** → Daily 3:45 PM IST
   ```bash
   python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 2 --use-yf
   python scripts/apply_models.py
   # Output: public/data/ticker/*.json + public/data/raw/*.csv
   ```

3. **`.github/workflows/train.yml`** → Weekly (Sunday)
   ```bash
   python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
   python scripts/train_regime_classifier.py
   python scripts/train_slippage_quantile.py
   python scripts/apply_models.py
   # Output: models/*.joblib + updated JSON predictions
   ```

---

## 📋 Complete Script List (In Order)

### **Initial Setup (Run Once)**
```bash
# 1. Get 503 tickers
python scripts/fetch_tickers.py
# → scripts/nifty500.txt

# 2. Generate all data
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
# → public/data/ticker/*.json (1,458 files)
# → public/data/raw/*.csv (503 files)

# 3. Train models
python scripts/train_regime_classifier.py
python scripts/train_slippage_quantile.py
# → models/*.joblib

# 4. Apply predictions
python scripts/apply_models.py
# → All JSONs with ML scores
```

---

### **What Each Script Outputs**

```
✅ fetch_tickers.py
   └─ scripts/nifty500.txt (503 tickers)

✅ fetch_spot_prices.py
   └─ public/data/live/spot_prices.json (50 KB, real-time prices)

✅ tradyxa_pipeline.py (batch mode)
   ├─ public/data/raw/{ticker}.csv (OHLCV data, incremental)
   └─ public/data/ticker/{ticker}.json (features, metrics, 9 tiles)

✅ train_regime_classifier.py
   ├─ models/rf_execution_regime.joblib
   └─ models/rf_execution_regime_metadata.json (training stats)

✅ train_slippage_quantile.py
   ├─ models/qr_slippage_q50.joblib
   └─ models/qr_slippage_q90.joblib

✅ apply_models.py
   └─ Updates all public/data/ticker/*.json with ML predictions
```

---

## 🔄 Recommended Schedule

| Time | Script | Frequency | Worker Count |
|------|--------|-----------|--------------|
| **9:15 AM - 3:30 PM IST** (every 30 min) | `fetch_spot_prices.py` | Daily (market hours) | N/A |
| **3:45 PM IST** (daily) | `tradyxa_pipeline.py (batch)` + `apply_models.py` | Weekdays | 2 |
| **Sunday midnight UTC** (weekly) | Full batch + training | Weekly | 4 |

---

## 💻 Dashboard Data Sources

**Each stock JSON contains:**
```json
{
  "metrics": {
    "spot_price": 1546.30,           ← From fetch_spot_prices.py / tradyxa_pipeline.py
    "volume": 2850000,                ← From CSV / Yahoo Finance
    "marketCap": "24.5T"              ← Computed from metrics
  },
  "volumeProfile": [...],             ← Generated tile data
  "candles": [...],                   ← Real OHLCV data
  "bollingerBands": [...],            ← Computed from candles
  "orderbook": [...],                 ← Generated from volatility
  "rollingAverages": [...],           ← Computed (MA5/20/50)
  "absorptionFlow": [...],            ← Buy/sell split
  "heatmap": [...],                   ← Market intensity patterns
  "histogram": [...],                 ← Returns distribution
  "slippageSamples": [...],           ← Volume-based costs
  "verdict": "UP",                    ← From tradyxa_pipeline.py
  "regime": 1,                        ← From train_regime_classifier.py
  "slippageQ50": 0.082,               ← From train_slippage_quantile.py
  "slippageQ90": 0.156                ← From train_slippage_quantile.py
}
```

---

## 🚀 Deployment Steps

1. **Push workflows to GitHub:**
   ```bash
   git add .github/workflows/*.yml
   git commit -m "Add GitHub Actions workflows for production"
   git push
   ```

2. **Ensure base data exists:**
   ```bash
   # All 1,458 JSON files should already be in public/data/ticker/
   ls public/data/ticker/*.json | wc -l  # Should show ~1,458
   ```

3. **Verify models exist:**
   ```bash
   ls models/*.joblib  # Should show 3 files
   ```

4. **Set up Cloudflare Pages:**
   - GitHub → Settings → Secrets
   - Add deployment webhook if needed
   - Auto-deploy on git push

5. **Test first workflow:**
   - GitHub → Actions → Daily Dashboard Update
   - Click "Run workflow" → Watch logs
   - Should complete in ~20 minutes

---

## 🔧 Python Dependencies (for GitHub Actions)

```bash
pip install pandas numpy yfinance scikit-learn joblib scipy tqdm
```

**Size:** ~500 MB (included in GitHub Actions Python 3.11)

---

## 📊 Expected Times

| Script | Single Stock | All 503 Stocks | Parallelization |
|--------|-------------|----------------|-----------------|
| `fetch_spot_prices.py` | N/A | <1 min | N/A |
| `tradyxa_pipeline.py` | ~5-6 min | 15-20 min | 2 workers (daily) |
| `tradyxa_pipeline.py` | ~5-6 min | 30-40 min | 4 workers (weekly) |
| `train_regime_classifier.py` | N/A | ~5 min | Automatic |
| `train_slippage_quantile.py` | N/A | ~5 min | Automatic |
| `apply_models.py` | N/A | ~2 min | Automatic |

---

## ✅ File Structure to Push to GitHub

```
.github/
└── workflows/
    ├── live_spot_prices.yml      ← Every 30 min
    ├── daily_update.yml          ← Daily 3:45 PM IST
    └── train.yml                 ← Weekly Sunday

public/
├── data/
│   ├── live/
│   │   └── spot_prices.json      ← Updated every 30 min
│   ├── raw/
│   │   ├── RELIANCE.NS.csv
│   │   ├── TCS.NS.csv
│   │   └── ... (503 files)
│   └── ticker/
│       ├── RELIANCE.NS.json      ← Updated daily
│       ├── TCS.NS.json
│       └── ... (503 files)

models/
├── rf_execution_regime.joblib         ← Updated weekly
├── rf_execution_regime_metadata.json
├── qr_slippage_q50.joblib
└── qr_slippage_q90.joblib

scripts/
├── nifty500.txt                  ← 503 tickers
├── fetch_tickers.py
├── fetch_spot_prices.py
├── data_manager.py
├── tradyxa_pipeline.py
├── train_regime_classifier.py
├── train_slippage_quantile.py
└── apply_models.py
```

---

## 🎯 Summary

**For Production Dashboard You Need:**

1. ✅ **1,458 JSON files** in `public/data/ticker/` (already generated)
2. ✅ **503 CSV files** in `public/data/raw/` (already generated)
3. ✅ **3 Trained models** in `models/` (already trained)
4. ✅ **3 GitHub Actions workflows** in `.github/workflows/` (already created)
5. ✅ **Live spot prices** in `public/data/live/spot_prices.json` (updated every 30 min)
6. ✅ **Cloudflare Pages** deployment (any git push triggers rebuild)

**Daily/Weekly Updates Automated:**
- Live prices: Every 30 minutes ✅
- Full data + ML: Daily at 3:45 PM IST ✅
- Model retraining: Weekly on Sunday ✅

**All Production-Ready! 🚀**
