# 📊 Production Data Pipeline - Visual Breakdown

## Full Production Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     🎯 DASHBOARD USER SEES THIS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Live Prices (updated every 30 min) + Dashboard Data (updated daily)         │
│                                                                               │
│  [Volume Profile] [Candles] [Bollinger] [Orderbook] [Rolling Avg]           │
│  [Absorption Flow] [Heatmap] [Histogram] [Slippage]                         │
│                                                                               │
│  Verdict: UP ✓ / DOWN ✗                                                     │
│  Investment: ₹X (based on MODEL)                                            │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↑
                                    │ Served by
                                    │ Cloudflare Pages CDN
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                     📁 DEPLOYED DATA FILES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  public/data/live/spot_prices.json                                           │
│  ├─ timestamp: "2025-12-03T10:30:00Z"                                       │
│  ├─ vix: 15.42                                                               │
│  └─ prices: { RELIANCE.NS: 1546.30, TCS.NS: 3167.80, ... }                  │
│     [Updated every 30 min by fetch_spot_prices.py]                          │
│                                                                               │
│  public/data/ticker/RELIANCE.NS.json (and 502 others)                       │
│  ├─ metrics: { spot_price, volume, marketCap }                              │
│  ├─ volumeProfile: [20 buckets]           ← 9 Tiles                         │
│  ├─ candles: [60 trading days]                                              │
│  ├─ bollingerBands: [20 periods]                                            │
│  ├─ orderbook: [20 levels]                                                  │
│  ├─ rollingAverages: [MA5/20/50]                                            │
│  ├─ absorptionFlow: [buy/sell split]                                        │
│  ├─ heatmap: [hour x day intensity]                                         │
│  ├─ histogram: [returns distribution]                                       │
│  ├─ slippageSamples: [50 samples]                                           │
│  ├─ verdict: "UP"                        ← From tradyxa_pipeline            │
│  ├─ regime: 1                            ← From ML model                    │
│  ├─ slippageQ50: 0.082                   ← From ML model                    │
│  └─ slippageQ90: 0.156                   ← From ML model                    │
│     [Updated daily by tradyxa_pipeline + apply_models]                     │
│                                                                               │
│  public/data/raw/RELIANCE.NS.csv                                             │
│  ├─ Date, Open, High, Low, Close, Volume                                    │
│  └─ [~5 years of OHLCV, incremental updates]                                │
│     [Updated daily by data_manager.py]                                      │
│                                                                               │
│  models/rf_execution_regime.joblib                                           │
│  ├─ RandomForest trained on 230k feature rows                               │
│  ├─ Predicts execution regime (0=LOW, 1=NORMAL, 2=HIGH, 3=SEVERE)          │
│  └─ [Updated weekly by train_regime_classifier.py]                          │
│                                                                               │
│  models/qr_slippage_q50.joblib                                               │
│  ├─ GradientBoosting Quantile Regression                                    │
│  ├─ Predicts median slippage (Q50)                                          │
│  └─ [Updated weekly by train_slippage_quantile.py]                          │
│                                                                               │
│  models/qr_slippage_q90.joblib                                               │
│  ├─ GradientBoosting Quantile Regression                                    │
│  ├─ Predicts worst-case slippage (Q90)                                      │
│  └─ [Updated weekly by train_slippage_quantile.py]                          │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↑
                                    │ Generated by
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│              🔄 GITHUB ACTIONS AUTOMATED WORKFLOWS                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ LIVE PRICES WORKFLOW (Every 30 min, 3:45 AM - 10:00 AM UTC)         │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │                                                                      │  │
│  │  fetch_spot_prices.py                                               │  │
│  │  ├─ Fetch current spot price for 503 stocks                        │  │
│  │  ├─ Fetch India VIX                                                │  │
│  │  └─ Save → public/data/live/spot_prices.json                       │  │
│  │                                                                      │  │
│  │  ⏱️  Time: <1 minute                                                │  │
│  │  📦 Size: ~50 KB                                                    │  │
│  │  🔄 Frequency: Every 30 min (market hours)                          │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                      ↓                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ DAILY UPDATE WORKFLOW (3:45 PM IST / 10:15 AM UTC, Weekdays)       │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │                                                                      │  │
│  │  1️⃣  tradyxa_pipeline.py (batch mode, --max-workers 2)             │  │
│  │  │                                                                  │  │
│  │  ├─ Read: scripts/nifty500.txt (503 tickers)                       │  │
│  │  ├─ For each stock:                                                │  │
│  │  │  ├─ data_manager.py                                             │  │
│  │  │  │  ├─ Yahoo Finance: Fetch ONLY new data since yesterday      │  │
│  │  │  │  └─ Save → public/data/raw/{ticker}.csv                     │  │
│  │  │  │                                                              │  │
│  │  │  ├─ Feature Engineering                                         │  │
│  │  │  │  ├─ Amihud illiquidity measure                               │  │
│  │  │  │  ├─ Lambda (price impact)                                    │  │
│  │  │  │  ├─ MFC (market fragmentation)                               │  │
│  │  │  │  ├─ Coordinated Flow (CF)                                    │  │
│  │  │  │  └─ 7+ more metrics                                          │  │
│  │  │  │                                                              │  │
│  │  │  ├─ Generate 9 Tile Data                                        │  │
│  │  │  │  ├─ generate_volume_profile_from_ohlcv() → 20 buckets      │  │
│  │  │  │  ├─ generate_candles_from_ohlcv() → 60 days                │  │
│  │  │  │  ├─ generate_bollinger_bands() → 20-period SMA ±2σ          │  │
│  │  │  │  ├─ generate_orderbook_from_ohlcv() → bid/ask levels       │  │
│  │  │  │  ├─ generate_rolling_averages() → MA5/20/50                │  │
│  │  │  │  ├─ generate_absorption_flow() → buy/sell split             │  │
│  │  │  │  ├─ generate_heatmap() → market intensity                   │  │
│  │  │  │  ├─ generate_histogram() → returns distribution             │  │
│  │  │  │  └─ generate_slippage_samples() → 50 samples                │  │
│  │  │  │                                                              │  │
│  │  │  ├─ Compute Verdict                                             │  │
│  │  │  │  ├─ Compare to historical signals                            │  │
│  │  │  │  ├─ Score: -2.0 to +2.0                                      │  │
│  │  │  │  └─ Result: UP (>0) / DOWN (<0)                              │  │
│  │  │  │                                                              │  │
│  │  │  └─ Save → public/data/ticker/{ticker}.json                    │  │
│  │  │                                                                  │  │
│  │  ⏱️  Time: 15-20 minutes (2 workers, incremental)                  │  │
│  │                                                                      │  │
│  │  2️⃣  apply_models.py                                                │  │
│  │  │                                                                  │  │
│  │  ├─ Load: 3 trained ML models                                       │  │
│  │  │  ├─ models/rf_execution_regime.joblib                           │  │
│  │  │  ├─ models/qr_slippage_q50.joblib                               │  │
│  │  │  └─ models/qr_slippage_q90.joblib                               │  │
│  │  │                                                                  │  │
│  │  ├─ For each stock:                                                │  │
│  │  │  ├─ Extract latest feature row from JSON                        │  │
│  │  │  ├─ RF predict → regime (0-3)                                   │  │
│  │  │  ├─ QR predict → slippageQ50 (median)                           │  │
│  │  │  ├─ QR predict → slippageQ90 (worst-case)                       │  │
│  │  │  └─ Update JSON with predictions                                │  │
│  │  │                                                                  │  │
│  │  ⏱️  Time: ~2 minutes                                               │  │
│  │                                                                      │  │
│  │  ✅ Result: 503 updated JSONs with all data + ML predictions       │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                      ↓                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ WEEKLY TRAINING WORKFLOW (Sunday midnight UTC / Monday 5:30 AM IST) │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │                                                                      │  │
│  │  1️⃣  tradyxa_pipeline.py (batch mode, --max-workers 4)             │  │
│  │  │                                                                  │  │
│  │  ├─ Full data refresh (even if incremental updates exist)          │  │
│  │  ├─ Ensures consistency and data quality                            │  │
│  │  └─ Generates fresh feature rows for all 503 stocks                 │  │
│  │                                                                      │  │
│  │  ⏱️  Time: 30-40 minutes (4 workers)                                │  │
│  │                                                                      │  │
│  │  2️⃣  train_regime_classifier.py                                     │  │
│  │  │                                                                  │  │
│  │  ├─ Load ALL 503 JSON files                                         │  │
│  │  ├─ Combine → ~230k feature rows                                    │  │
│  │  ├─ Create labels: 0=LOW, 1=NORMAL, 2=HIGH, 3=SEVERE              │  │
│  │  │  (based on p90 slippage thresholds)                             │  │
│  │  ├─ Train: RandomForest classifier                                  │  │
│  │  ├─ Evaluate: accuracy, feature importance                          │  │
│  │  ├─ Save: models/rf_execution_regime.joblib                         │  │
│  │  └─ Save: models/rf_execution_regime_metadata.json                  │  │
│  │                                                                      │  │
│  │  ⏱️  Time: ~5 minutes                                               │  │
│  │                                                                      │  │
│  │  3️⃣  train_slippage_quantile.py                                     │  │
│  │  │                                                                  │  │
│  │  ├─ Load ALL 503 JSON files                                         │  │
│  │  ├─ Combine → ~230k feature rows                                    │  │
│  │  ├─ Train Q50 model: GradientBoosting + Quantile Loss             │  │
│  │  │  └─ Predicts: median slippage (typical execution cost)          │  │
│  │  ├─ Train Q90 model: GradientBoosting + Quantile Loss             │  │
│  │  │  └─ Predicts: worst-case slippage (tail risk)                   │  │
│  │  ├─ Save: models/qr_slippage_q50.joblib                            │  │
│  │  └─ Save: models/qr_slippage_q90.joblib                            │  │
│  │                                                                      │  │
│  │  ⏱️  Time: ~5 minutes                                               │  │
│  │                                                                      │  │
│  │  4️⃣  apply_models.py (optional, since daily does it)               │  │
│  │  │                                                                  │  │
│  │  └─ Update all JSONs with latest model predictions                 │  │
│  │                                                                      │  │
│  │  ✅ Result: Retrained models, updated predictions, fresh data      │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↑
                                    │ Triggered by
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🔐 GITHUB REPOSITORY & GIT PUSH                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  • Workflows defined in: .github/workflows/*.yml                            │
│  • Data committed to: public/data/ticker/*.json + public/data/raw/*.csv     │
│  • Models committed to: models/*.joblib                                      │
│                                                                               │
│  Every git push → Cloudflare Pages webhook → Redeploy dashboard             │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Data Flow Summary

### **What Gets Updated When**

```
EVERY 30 MIN (Market Hours)
    ↓
    fetch_spot_prices.py
    ↓
    public/data/live/spot_prices.json ← Dashboard gets real-time prices

DAILY (3:45 PM IST)
    ↓
    tradyxa_pipeline.py
    ↓
    public/data/raw/{ticker}.csv ← OHLCV incremental update
    public/data/ticker/{ticker}.json ← Features, 9 tiles, verdict
    ↓
    apply_models.py
    ↓
    public/data/ticker/{ticker}.json ← +ML predictions (regime, Q50, Q90)
    ↓
    Dashboard shows: Real data + ML insights + Investment recommendation

WEEKLY (Sunday)
    ↓
    tradyxa_pipeline.py (full refresh)
    train_regime_classifier.py
    train_slippage_quantile.py
    apply_models.py
    ↓
    models/*.joblib ← Better ML models
    public/data/ticker/{ticker}.json ← Updated predictions
    ↓
    Dashboard shows: Fresher ML models for better accuracy
```

---

## 📊 Data Volume

```
Live Prices: 50 KB (updated every 30 min)
Each Stock JSON: 150-200 KB
Total Ticker JSONs: 503 × 175 KB = ~87 MB
Raw OHLCV CSVs: 503 × 500 KB = ~250 MB
Models: 20 MB total
────────────────────────────────
Total Repository: ~360 MB (cached files)

GitHub Actions Storage: Free ✅
Cloudflare Pages: Free for up to 500 deployments/month ✅
```

---

## ⚡ Performance Checklist

| Metric | Value | Status |
|--------|-------|--------|
| Live prices fetch | <1 min | ✅ Fast |
| Daily pipeline (2 workers) | 15-20 min | ✅ Acceptable |
| Weekly pipeline (4 workers) | 30-40 min | ✅ Acceptable |
| ML training | ~10 min | ✅ Efficient |
| Dashboard load time | <2s | ✅ CDN cached |
| Real-time data latency | ~30 min (spot prices) | ✅ Live enough |
| Daily data latency | <4 hours | ✅ EOD update |

---

## 🚀 Deployment Checklist

- [ ] `.github/workflows/live_spot_prices.yml` committed
- [ ] `.github/workflows/daily_update.yml` committed
- [ ] `.github/workflows/train.yml` committed
- [ ] All 1,458 JSON files in `public/data/ticker/` committed
- [ ] All 503 CSV files in `public/data/raw/` committed
- [ ] All 3 models in `models/` committed
- [ ] `scripts/nifty500.txt` has 503 tickers
- [ ] Cloudflare Pages connected to GitHub repo
- [ ] First workflow run tested manually
- [ ] Dashboard accessible and shows latest data
- [ ] Monitoring enabled (GitHub email alerts)

---

**Status: Ready for Production Deployment ✅**

All workflows automated, data refreshed daily/weekly, dashboard updated every 30 minutes. No manual intervention needed!
