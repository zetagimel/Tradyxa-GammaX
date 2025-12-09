# TRADYXA AZTRYX - Complete System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TRADYXA AZTRYX SYSTEM FLOW                          │
└─────────────────────────────────────────────────────────────────────────────┘

USER DASHBOARD (React Frontend)
    ↓ (30-second poll)
    
BACKEND SERVER (Express.js)
    ↓
PYTHON PIPELINE (Batch Processing)
    ↓
DATA SOURCES & ML MODELS
    ↓
VISUALIZATION (9 Market Tiles)
```

---

## COMPLETE DATA FLOW (Step-by-Step)

### **PHASE 1: DATA COLLECTION** 📊

#### 1.1 Live Spot Price Fetching (Every 30 minutes)
```
Real-time Market Data
        ↓
    yfinance
        ↓
scripts/fetch_spot_prices.py
        ↓
public/data/live/spot_prices.json
{
  "spot_prices": {
    "CHAMBLFERT.NS": {"spot_price": 435.15, "change_percent": 0.35},
    "RELIANCE.NS": {"spot_price": 1537, "change_percent": 1.2},
    "^NSEI": {"spot_price": 23450, "change_percent": 0.8}
  },
  "india_vix": {
    "vix": 16.5,  // Stable for a day (updated once daily)
    "last_update": "2025-12-03T09:15:00Z"
  }
}
```

**Purpose**: Gets current market price + change % for each stock + India VIX volatility index

---

#### 1.2 Historical OHLCV Data (5-year history)
```
Daily Market Data (OHLCV)
        ↓
    yfinance
        ↓
scripts/data_manager.py (Cache + Incremental Update)
        ↓
public/data/raw/{TICKER}.csv
┌──────────────────────────────────────────────────────────┐
│ Date       │ Open  │ High  │ Low   │ Close │ Volume      │
├──────────────────────────────────────────────────────────┤
│ 2020-01-01 │ 100   │ 105   │ 99    │ 102   │ 1,000,000   │
│ 2020-01-02 │ 102   │ 108   │ 101   │ 105   │ 1,200,000   │
│ ...        │ ...   │ ...   │ ...   │ ...   │ ...         │
│ 2025-12-03 │ 435   │ 442   │ 434   │ 435.15│ 2,500,000   │
└──────────────────────────────────────────────────────────┘
```

**Purpose**: Historical trading data for calculating technical indicators

---

### **PHASE 2: DATA PROCESSING & FEATURE ENGINEERING** ⚙️

#### 2.1 Python Pipeline Processing
**File**: `scripts/tradyxa_pipeline.py`

**For each of 503 stocks, it:**

```python
1. READ OHLCV DATA
   └─ Get 5-year historical data from CSV

2. COMPUTE TECHNICAL FEATURES
   └─ Calculate for each candle:
      • Amihud (illiquidity measure)
      • Lambda (effective spread)
      • MFC (market friction coefficient)
      • Volatility (price volatility)
      • Volume Z-score (unusual volume detection)
      • Returns distribution
      • Time of day (TOD)
      • HLC ratio (high-low-close range)

3. GENERATE 9 MARKET TILES
   ├─ Volume Profile
   │  └─ Distribution of prices over 60-day window
   │     (how much volume traded at each price level)
   │
   ├─ Candles (OHLCV Chart)
   │  └─ Last 60 trading days in candlestick format
   │
   ├─ Bollinger Bands
   │  └─ 20-period SMA ± 2 standard deviations
   │     (shows overbought/oversold conditions)
   │
   ├─ Orderbook Depth
   │  └─ Simulated bid/ask levels based on volatility
   │
   ├─ Rolling Averages
   │  └─ MA5, MA20, MA50 (trend indicators)
   │
   ├─ Absorption Flow
   │  └─ Buy vs Sell volume accumulation over time
   │
   ├─ Activity Heatmap
   │  └─ 168-cell grid (7 days × 24 hours)
   │     Shows peak trading times
   │
   ├─ Returns Distribution
   │  └─ Histogram of daily returns
   │     (market stability indicator)
   │
   └─ Slippage Samples
      └─ Expected vs actual execution prices
         for different order sizes (100K, 250K, 500K, 1M)

4. OUTPUT JSON
   └─ Comprehensive ticker JSON with all 9 tiles
      + metrics + features
```

**Output**: `public/data/ticker/{TICKER}.json` (175 KB each)

---

### **PHASE 3: ML MODEL PREDICTIONS** 🤖

#### 3.1 Regime Classification Model
**File**: `models/rf_execution_regime.joblib`

```
Input Features (9):
  • Amihud
  • Lambda
  • MFC
  • Vol Z-score
  • Volatility
  • Volume
  • Returns
  • HLC Ratio
  • Time of Day
      ↓
Random Forest Model (Trained on historical data)
      ↓
Output: EXECUTION_REGIME (3 classes)
  • 0 = Low Friction (Easy to trade)
  • 1 = Normal (Average conditions)
  • 2 = High Friction (Difficult to trade)
```

**Purpose**: Classifies current market microstructure conditions

---

#### 3.2 Slippage Quantile Regression Models
**Files**: 
- `models/qr_slippage_q50.joblib` (Median slippage)
- `models/qr_slippage_q90.joblib` (90th percentile slippage)

```
Input Features (same 9 as regime model)
      ↓
Quantile Regression Model
      ↓
Output: EXPECTED SLIPPAGE (%)
  • q50 = Median (50% of time below this)
  • q90 = 90th percentile (90% of time below this)
```

**Purpose**: Predicts execution cost based on current market conditions

---

#### 3.3 Application to All Stocks
**File**: `scripts/apply_models.py`

```
For each ticker JSON:
  1. Extract latest technical features
  2. Feed to regime model → get execution regime label
  3. Feed to slippage models → get q50 & q90 predictions
  4. Update JSON with ML predictions
  5. Add to metrics section

Result: Each ticker JSON now has ML predictions
```

---

### **PHASE 4: VERDICT GENERATION** 📈

#### 4.1 Multi-Factor Analysis
**File**: `scripts/tradyxa_pipeline.py` (function: `compute_verdict`)

```
For each stock, compute 5-component verdict:

1. MOMENTUM COMPONENT
   Input: Rolling averages (MA5, MA20, MA50)
   Logic: If MA5 > MA20 > MA50 → Bullish (weight: 0.2)

2. VOLATILITY COMPONENT
   Input: Bollinger Bands, Vol Z-score
   Logic: Price near upper band + high vol → Bullish (weight: 0.15)

3. MICROSTRUCTURE COMPONENT
   Input: ML execution regime label
   Logic: Low friction regime → Better conditions (weight: 0.25)

4. ABSORPTION COMPONENT
   Input: Buy vs Sell flow
   Logic: More buy flow → Bullish (weight: 0.2)

5. SLIPPAGE COMPONENT
   Input: Predicted slippage expectation
   Logic: Low slippage → Better for execution (weight: 0.2)

COMBINED VERDICT:
  Weighted sum of all 5 components (each 0-100 scale)
  ↓
  Result: BULLISH (70 points) / BEARISH (30) / NEUTRAL (50)
  
  Direction determined by:
    > 60 = BULLISH
    < 40 = BEARISH
    40-60 = NEUTRAL
```

---

### **PHASE 5: DATA SERVING TO FRONTEND** 🖥️

#### 5.1 Backend Routes
**File**: `server/routes.ts`

```
GET /api/ticker/{TICKER}
    ↓
Read from JSON file
    ↓
Get live spot price from spot_prices.json
    ↓
Combine with cached data
    ↓
Return TickerData {
  "ticker": "CHAMBLFERT",
  "metrics": {
    "spotPrice": 435.15,
    "spotChange": 1.55,
    "spotChangePercent": 0.35,
    "vix": 16.5,
    "verdict": "BULLISH",
    "slippageExpectation": 0.08,
    "ml_regime_label": 0,  // Low friction
    "ml_regime_prob": [0.8, 0.15, 0.05]  // Confidence
  },
  "volumeProfile": [...],
  "candles": [...],
  "bollingerBands": [...],
  "orderbook": [...],
  "rollingAverages": [...],
  "absorptionFlow": [...],
  "heatmap": [...],
  "histogram": [...],
  "slippageSamples": [...]
}
```

#### 5.2 Caching Strategy
```
Ticker Cache (60-second TTL):
  • Stores full ticker JSON in memory
  • Expires after 60 seconds
  • Reduces file I/O for frequent requests

Live Spot Price Update (30-second poll):
  • Dashboard polls every 30 seconds
  • Gets latest spot_prices.json
  • Merges with cached tile data
  • Shows live price with historical tiles
```

---

### **PHASE 6: FRONTEND VISUALIZATION** 📊

#### 6.1 Dashboard Component Flow
**File**: `client/src/pages/Dashboard.tsx`

```
React Component
    ↓
useQuery (React Query)
    ├─ Poll every 30 seconds: /api/ticker/{TICKER}
    └─ Get full data: /api/ticker/{TICKER}/full
        ↓
State Management
    ├─ Selected Ticker
    ├─ Notional Size (100K-1M)
    ├─ Theme (light/dark)
    └─ Inspector/Explain modals
        ↓
Render 9 Tiles + Metrics
    ├─ VerdictTile (BULLISH/BEARISH/NEUTRAL)
    ├─ GaugeTile (VIX indicator)
    ├─ HistogramTile (returns distribution)
    ├─ HeatmapTile (activity patterns)
    ├─ CandlesWithBands (price action)
    ├─ BarWithRolling (volume + MA)
    ├─ ScatterSlippage (execution costs)
    ├─ StackedAreaAbsorption (flow direction)
    ├─ VolumeProfile (price support/resistance)
    ├─ OrderbookDepth (liquidity)
    └─ NumericCards (key metrics)
```

---

## DATA STRUCTURE HIERARCHY

```
TRADYXA_AZTRYX/
│
├── public/data/
│   ├── live/
│   │   └── spot_prices.json          ← Live spot prices (every 30 min)
│   │       {
│   │         "spot_prices": {...},
│   │         "india_vix": {...}
│   │       }
│   │
│   ├── raw/
│   │   └── {TICKER}.csv              ← 5-year OHLCV history
│   │       (500+ files, incremental updates)
│   │
│   └── ticker/
│       └── {TICKER}.json             ← COMPLETE ANALYSIS
│           {
│             "meta": {...},
│             "metrics": {
│               "spotPrice": 435.15,
│               "vix": 16.5,
│               "verdict": "BULLISH",
│               "ml_regime_label": 0,
│               ...
│             },
│             "features_head": {...},  ← Last 500 candles + features
│             "volumeProfile": [...],
│             "candles": [...],
│             "bollingerBands": [...],
│             "orderbook": [...],
│             "rollingAverages": [...],
│             "absorptionFlow": [...],
│             "heatmap": [...],
│             "histogram": [...],
│             "slippageSamples": [...]
│           }
│
├── models/
│   ├── rf_execution_regime.joblib    ← Regime classifier (Random Forest)
│   ├── qr_slippage_q50.joblib        ← Median slippage (Quantile Reg)
│   └── qr_slippage_q90.joblib        ← P90 slippage (Quantile Reg)
│
└── scripts/
    ├── tradyxa_pipeline.py           ← Main processing engine
    ├── data_manager.py               ← OHLCV data fetcher
    ├── fetch_spot_prices.py          ← Live spot prices
    ├── apply_models.py               ← ML prediction application
    └── train_*.py                    ← ML model training
```

---

## KEY INSIGHTS

### ✅ What Happens Every 30 Minutes
1. **Fetch Live Spot Price** from yfinance
2. **Store in** `spot_prices.json`
3. **Dashboard polls** and displays latest price
4. **9 Tiles remain static** (from last batch run)

### ✅ What Happens During Batch Run (Daily/On-Demand)
1. **Fetch 5-year OHLCV** data for all 503 stocks
2. **Generate 9 market tiles** for each stock
3. **Apply ML models** to get predictions
4. **Compute verdicts** based on 5 factors
5. **Save complete JSON** for each ticker
6. **Cache for 60 seconds** on next request

### ✅ How ML Enhances Decision-Making
- **Regime Classification**: Tells if market is liquid (easy to trade) or illiquid (hard to trade)
- **Slippage Prediction**: Estimates execution cost before placing order
- **Verdict Generation**: Combines all signals into actionable buy/sell/hold signal
- **Confidence Scoring**: Shows how confident the model is in its prediction

### ✅ Real vs Synthetic Data
- **Real Data**: OHLCV from yfinance (5 years history)
- **Real Data**: Live spot prices (every 30 min)
- **Real Data**: India VIX (once daily)
- **Computed/Generated**: Volume Profile, Orderbook (derived from real data)
- **Model-Driven**: Slippage prediction, Regime classification (ML trained on real data)
- **Deterministic**: Bollinger Bands, Moving Averages, Absorption Flow (calculated from real data)

---

## PERFORMANCE OPTIMIZATION

```
Caching Strategy:
  └─ 60-second TTL on ticker JSON files
     Reduces file I/O from 9+ reads → 1 read per 60 sec

Live Price Polling:
  └─ Dashboard requests every 30 seconds
     Merges live spot with cached tile data
     Fast response, minimal overhead

Batch Processing:
  └─ 4 parallel workers for 503 stocks
     ~20 seconds per stock in pipeline
     Total: ~15-20 minutes for full batch

File Size:
  └─ 175 KB per ticker JSON
     503 stocks × 175 KB = ~88 MB total
     Fits easily in memory cache
```

---

## SUMMARY WORKFLOW

```
┌─────────────────────────────────────────────────────────────┐
│ USER OPENS DASHBOARD                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │ Browser polls every 30 sec  │
         │ GET /api/ticker/CHAMBLFERT  │
         └──────────────┬──────────────┘
                        │
                        ▼
         ┌─────────────────────────────┐
         │ Backend Express Server      │
         │ 1. Read JSON from cache     │
         │ 2. Get live spot price      │
         │ 3. Merge + return           │
         └──────────────┬──────────────┘
                        │
                        ▼
         ┌─────────────────────────────┐
         │ Complete Ticker Data        │
         │ • Current spot: ₹435.15     │
         │ • 9 market tiles            │
         │ • Verdict: BULLISH          │
         │ • ML predictions            │
         └──────────────┬──────────────┘
                        │
                        ▼
         ┌─────────────────────────────┐
         │ Frontend Renders            │
         │ 9 Interactive Tiles         │
         │ + Verdict + Metrics         │
         └─────────────────────────────┘
```

---

## BEHIND THE SCENES (Batch Pipeline)

```
┌──────────────────────────────────────────────────┐
│ DAILY BATCH PROCESSING (tradyxa_pipeline.py)    │
└───────────────────┬──────────────────────────────┘
                    │
        ┌───────────┴────────────┬────────────────┐
        ▼                        ▼                ▼
    [503 Stocks]           [4 Workers]     [Parallel]
        │
    For Each Ticker:
        │
        ├─ 1. Fetch OHLCV data (5 years)
        │
        ├─ 2. Compute 9+ technical features
        │
        ├─ 3. Generate 9 tiles
        │   ├─ Volume Profile (from price histogram)
        │   ├─ Candles (OHLCV bars)
        │   ├─ Bollinger Bands (SMA ± 2σ)
        │   ├─ Orderbook (from volatility)
        │   ├─ Rolling Averages (MA5/20/50)
        │   ├─ Absorption Flow (buy/sell split)
        │   ├─ Heatmap (time intensity grid)
        │   ├─ Histogram (returns distribution)
        │   └─ Slippage Samples (execution costs)
        │
        ├─ 4. Apply ML models
        │   ├─ Regime classification (RF model)
        │   ├─ Slippage prediction (QR models)
        │   └─ Add probabilities/confidence
        │
        ├─ 5. Compute verdict
        │   ├─ Score momentum, volatility, microstructure
        │   ├─ Weight factors: (0.2, 0.15, 0.25, 0.2, 0.2)
        │   └─ Output: BULLISH/BEARISH/NEUTRAL + confidence
        │
        └─ 6. Save JSON to disk
            └─ public/data/ticker/{TICKER}.json
```

---

## KEY TAKEAWAY

**Tradyxa Aztryx = Smart Dashboard That Combines:**

1. **Real-Time Data**: Live spot prices every 30 min
2. **Historical Analysis**: 5-year OHLCV data processed into 9 tiles
3. **ML Intelligence**: Regime classification + slippage prediction
4. **Smart Verdicts**: Multi-factor analysis → BUY/SELL/HOLD signals
5. **Fast Delivery**: Cached, optimized backend serving to React frontend
6. **Visual Excellence**: 9 interactive market tiles for complete picture

**Result**: A comprehensive stock analysis dashboard that helps traders make informed decisions faster!
