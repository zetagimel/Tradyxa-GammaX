# THE COMMAND EXPLAINED VISUALLY

## 🎯 Main Command Anatomy

```
┌─────────────────────────────────────────────────────────────────────┐
│ python scripts/tradyxa_pipeline.py --mode batch_run                 │
│         --tickers-file scripts/nifty500.txt                         │
│         --max-workers 4 --use-yf                                    │
└─────────────────────────────────────────────────────────────────────┘
         ↓              ↓                ↓              ↓         ↓
      script        operation         input file     parallelism  data
```

### Breaking It Down:

**Part 1: Script Location**
```
python scripts/tradyxa_pipeline.py
   ↓
   Runs the Python pipeline script
   Location: c:\...\Tradyxa Aztryx\scripts\tradyxa_pipeline.py
   Size: 970 lines of code
```

**Part 2: Operation Mode**
```
--mode batch_run
   ↓
   Options:
   • batch_run      ← Process all 503 stocks (THIS ONE)
   • run_all        ← Process one specific ticker
   • sample_data    ← Generate synthetic data for testing
```

**Part 3: Input File**
```
--tickers-file scripts/nifty500.txt
   ↓
   File containing list of tickers:
   ^NSEI
   ^NSEBANK
   360ONE.NS
   3MINDIA.NS
   ... (503 total)
   ZEALOUSTEEL.NS
```

**Part 4: Worker Threads**
```
--max-workers 4
   ↓
   Process 4 tickers in PARALLEL (simultaneously)
   
   TIME:   0-3s     3-6s     6-9s     9-12s
           ────    ────    ────    ────
   Worker 1: NTPC   ACC    BAJAJ   INFY
   Worker 2: TCS    WIPRO  MARUTI  TECH
   Worker 3: RELIANCE   HDFC   ICICI   AXIS
   Worker 4: SUNPHARMA   DMART   L&T   Pharma
   
   Result: ~3s per stock × 503 stocks ÷ 4 workers = ~6-7 minutes
```

**Part 5: Data Source**
```
--use-yf
   ↓
   Fetch from Yahoo Finance (live data)
   If omitted: Use cached CSV only
   
   ✓ Yahoo Finance = Fresh, latest data
   ✗ Cached only = Might be 1-2 days old
```

---

## 🔄 FULL EXECUTION FLOW

```
┌──────────────────────────────────────────┐
│   START BATCH COMMAND                    │
│   503 tickers, 4 workers                 │
└────────────────┬─────────────────────────┘
                 ↓
        ┌────────────────────┐
        │  Read nifty500.txt │
        │  (503 tickers)     │
        └────────────┬───────┘
                     ↓
        ┌────────────────────────────────────────┐
        │  Create Thread Pool (4 workers)        │
        │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
        │  │Wrk 1 │ │Wrk 2 │ │Wrk 3 │ │Wrk 4 │  │
        │  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘  │
        └─────┼────────┼────────┼────────┼───────┘
              │        │        │        │
              ↓        ↓        ↓        ↓
         Ticker 1  Ticker 2  Ticker 3  Ticker 4
         ║         ║         ║         ║
         ║         ║         ║         ║
         ∨         ∨         ∨         ∨
      ┌──────────────────────────────────────────┐
      │  FOR EACH TICKER:                        │
      │                                          │
      │  1. Fetch OHLCV (CSV or Yahoo)          │
      │     ↓                                    │
      │  2. Compute Features (9 metrics)        │
      │     ↓                                    │
      │  3. Generate Tiles (9 visualizations)   │
      │     - Volume Profile                    │
      │     - Candles                           │
      │     - Bollinger Bands                   │
      │     - Orderbook                         │
      │     - Rolling Averages                  │
      │     - Absorption Flow                   │
      │     - Heatmap                           │
      │     - Histogram                         │
      │     - Slippage                          │
      │     ↓                                    │
      │  4. Calculate Verdict                   │
      │     ↓                                    │
      │  5. Write 3 JSON Files                  │
      │     - {TICKER}.json                     │
      │     - {TICKER}_slippage.json            │
      │     - {TICKER}_monte_slippage.json      │
      │     ↓                                    │
      │  Done! (~3-5 seconds)                   │
      └──────────────────────────────────────────┘
              │        │        │        │
              └────┬───┴────┬───┴────┬───┘
                   ↓        ↓        ↓
              Next batch of 4 tickers...
              (Worker pool auto-assigns)
              
              ... repeat 125 times ...
              
         When all 503 complete:
              │
              ↓
      ┌─────────────────────┐
      │  BATCH COMPLETE ✓   │
      │ 1,509 JSON files    │
      │  updated in         │
      │  ~6-7 minutes       │
      └─────────────────────┘
```

---

## 📊 TIMELINE EXAMPLE

```
TIME: 15:13:18 ──────────────────────────────────────────────── 15:19:50

Step 1: 0s - Start batch
  └─ Create 4 worker threads
  └─ Read 503 tickers from file

Step 2: 0-3s - First batch (tickers 1-4)
  └─ Worker 1: ^NSEI        │
  └─ Worker 2: ^NSEBANK     │ Processing
  └─ Worker 3: 360ONE.NS    │ in parallel
  └─ Worker 4: 3MINDIA.NS   │

Step 3: 3-6s - Second batch (tickers 5-8)
  └─ Worker 1: ABB.NS
  └─ Worker 2: ACC.NS
  └─ Worker 3: ACE.NS
  └─ Worker 4: ACMESOLAR.NS
  
      ... (repeat for 125 iterations) ...

Step 4: 390s (~6:30) - Final batch (tickers 500-503)
  └─ Worker 1: ZEALOUSTEEL.NS
  └─ Worker 2: ZYDUSLIFE.NS
  └─ Worker 3: (empty)
  └─ Worker 4: (empty)

Step 5: 400s (~6:40) - DONE!
  └─ All 1,509 JSON files updated
  └─ Show summary: "100%|██████████| 503/503"
```

---

## 🎯 WHAT EACH WORKER DOES (SERIAL - one ticker at a time)

```
WORKER 1 PROCESSING NTPC.NS:
├─ Fetch CSV from cache
├─ Read 5-year OHLCV history (1,240 trading days)
├─ Compute Features
│  ├─ Amihud liquidity
│  ├─ Lambda impact
│  ├─ Market fragmentation (MFC)
│  ├─ Volume Z-score
│  ├─ 20-day volatility
│  ├─ Coordinated flow
│  ├─ Daily returns
│  ├─ High-Low-Close ratio
│  └─ Time-of-day analysis
├─ Generate Tiles
│  ├─ Volume Profile: Last 60 days → 20 price buckets
│  ├─ Candles: Last 60 days → 60 OHLC bars
│  ├─ Bollinger Bands: 20-day SMA ± 2σ
│  ├─ Orderbook: Synthetic bids/asks
│  ├─ Rolling Averages: MA5, MA20, MA50
│  ├─ Absorption Flow: Buy vs Sell volume
│  ├─ Heatmap: 24h × 7d trading intensity grid
│  ├─ Histogram: Returns distribution (20 bins)
│  └─ Slippage: 50 execution cost samples
├─ Calculate Metrics
│  ├─ Momentum score (45% weight)
│  ├─ Flow score (25% weight)
│  ├─ Liquidity score (15% weight)
│  └─ Cost score (15% weight)
├─ Compute Verdict
│  ├─ Direction: UP / DOWN / NEUTRAL
│  ├─ Points: ±15 (price move estimate)
│  ├─ Confidence: 0-100%
│  └─ Recommendation: Buy, Sell, Wait
├─ Write JSON Files
│  ├─ public/data/ticker/NTPC.NS.json (main)
│  ├─ public/data/ticker/NTPC.NS_slippage.json
│  └─ public/data/ticker/NTPC.NS_monte_slippage.json
└─ Time: ~3-5 seconds per stock

→ Next ticker: ACC.NS (repeat)
```

---

## 💾 OUTPUT STRUCTURE

```
After Batch Completes:

public/data/ticker/
├── ^NSEI.json                        (Index)
├── ^NSEI_slippage.json
├── ^NSEI_monte_slippage.json
├── ^NSEBANK.json                     (Index)
├── ^NSEBANK_slippage.json
├── ^NSEBANK_monte_slippage.json
├── 360ONE.NS.json                    (Stock)
├── 360ONE.NS_slippage.json
├── 360ONE.NS_monte_slippage.json
├── 3MINDIA.NS.json
├── 3MINDIA.NS_slippage.json
├── 3MINDIA.NS_monte_slippage.json
│
... 503 stocks × 3 files each = 1,509 files total ...
│
├── ZEALOUSTEEL.NS.json
├── ZEALOUSTEEL.NS_slippage.json
├── ZEALOUSTEEL.NS_monte_slippage.json
├── ZYDUSLIFE.NS.json
├── ZYDUSLIFE.NS_slippage.json
└── ZYDUSLIFE.NS_monte_slippage.json

Total Size: ~225 MB
```

---

## 🔍 JSON FILE CONTENT EXAMPLE

```
public/data/ticker/NTPC.NS.json
{
  "meta": {
    "ticker": "NTPC.NS",
    "last_updated": "2025-12-03T15:20:45Z",
    "data_source": "yfinance"
  },
  "metrics": {
    "spot_price": 322.05,          ← Live spot
    "volatility": 0.015,           ← 20-day volatility
    "liquidity_depth_proxy": 0.8,
    "coordinated_flow": 1.2
  },
  "volumeProfile": [
    {"price": 321.0, "volume": 152000, "buyVolume": 90000, "sellVolume": 62000},
    {"price": 323.5, "volume": 189000, "buyVolume": 115000, "sellVolume": 74000},
    ...
    {"price": 348.0, "volume": 98000, "buyVolume": 45000, "sellVolume": 53000}
  ],
  "candles": [
    {"date": "2025-09-09", "open": 325.0, "high": 329.5, "low": 321.0, "close": 327.0, "volume": 2500000},
    ...
    {"date": "2025-12-03", "open": 319.0, "high": 325.5, "low": 318.0, "close": 322.05, "volume": 3200000}
  ],
  "bollingerBands": [...],
  "orderbook": [...],
  "rollingAverages": [...],
  "absorptionFlow": [...],
  "heatmap": [...],
  "histogram": [...],
  "slippageSamples": [...],
  "verdict": {
    "direction": "UP",
    "points": 12.50,
    "confidence": 0.75,
    "explanation": "Strong bullish momentum with good liquidity..."
  }
}
```

---

## ⚡ TL;DR

**Command:**
```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx"
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
```

**What happens:**
- 4 workers process 503 stocks in parallel
- Each stock takes ~3-5 seconds
- Total: ~6-7 minutes
- Output: 1,509 JSON files with fresh market tiles

**Result:**
- ✅ All 503 stocks regenerated
- ✅ 11 corrupted stocks fixed
- ✅ Tiles show correct 60-day price ranges
- ✅ Verdicts recalculated with fresh data
