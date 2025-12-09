# DATA SOURCE DOCUMENTATION - Tradyxa Aztryx
## Where Each Tile's Data Comes From

---

## 🎯 PRIMARY DATA SOURCE
**All tiles derive from a single source: Yahoo Finance (yfinance)**

```
Yahoo Finance (yfinance)
        ↓
   5-Year OHLCV Data
        ↓
CSV Cache (public/data/raw/{TICKER}.csv)
        ↓
Python Pipeline (tradyxa_pipeline.py)
        ↓
9 Market Tiles (Generated from OHLCV)
        ↓
JSON Output (public/data/ticker/{TICKER}.NS.json)
```

---

## 📊 EACH TILE EXPLAINED

### 1. **VOLUME PROFILE** 
**File:** `tradyxa_pipeline.py` → `generate_volume_profile_from_ohlcv()` (Line 484)

**Data Source:**
- **Input:** Last 60 days of OHLCV data from Yahoo Finance
- **Processing:**
  - Divides price range into 20 buckets (price levels)
  - For each day's candle, distributes volume across price levels it touched
  - Determines buy/sell split based on candle direction (green=more buy, red=more sell)
  - Shows where most trading happened in the 60-day window

**What you see:**
- Price levels on Y-axis (₹320 → ₹350 range for NTPC)
- Volume at each level as bar height
- Buy volume (green) vs Sell volume (red)

**Formula:**
```python
df = ohlcv.tail(60)  # Last 60 trading days
min_price = df['Low'].min()
max_price = df['High'].max()
price_levels = np.linspace(min_price, max_price, 20)  # 20 buckets

# For each day, distribute its volume across price levels
if close > open:
    buy_ratio = 70%  # More buying on up candles
else:
    buy_ratio = 30%  # Less buying on down candles
```

---

### 2. **CANDLES WITH BOLLINGER BANDS**
**File:** `tradyxa_pipeline.py` → Lines 543-591

**Data Sources:**

**A) Candles** (Line 543 - `generate_candles_from_ohlcv`)
- **Input:** Last 60 trading days OHLC data
- **Output:** 60 candlestick bars showing Open, High, Low, Close for each day

**B) Bollinger Bands** (Line 563 - `generate_bollinger_bands`)
- **Input:** Last 80 days of Close prices (60 + 20 day SMA window)
- **Calculation:**
  ```python
  SMA = Close.rolling(20).mean()          # 20-day Simple Moving Average
  Std = Close.rolling(20).std()           # 20-day Standard Deviation
  Upper Band = SMA + (2 × Std)            # +2 standard deviations
  Lower Band = SMA - (2 × Std)            # -2 standard deviations
  ```
- **Interpretation:** Price bouncing between bands shows support/resistance

---

### 3. **PRICE WITH ROLLING AVERAGES**
**File:** `tradyxa_pipeline.py` → `generate_rolling_averages()` (Line 629)

**Data Source:**
- **Input:** Last 70 days of Close prices
- **Calculation:**
  ```python
  MA5 = Close.rolling(5).mean()           # 5-day Moving Average
  MA20 = Close.rolling(20).mean()         # 20-day Moving Average
  MA50 = Close.rolling(50).mean()         # 50-day Moving Average
  ```
- **Shows:** Trend direction
  - If Close > MA50 > MA20 > MA5 = Strong uptrend
  - If Close < MA5 < MA20 < MA50 = Strong downtrend

---

### 4. **ORDERBOOK DEPTH**
**File:** `tradyxa_pipeline.py` → `generate_orderbook_from_ohlcv()` (Line 593)

**Data Source:**
- **Input:** Last 20 days of Close prices, current price, and volatility
- **Synthetic Generation** (Not real orderbook - market microstructure simulation):
  ```python
  recent_volatility = Close.pct_change().tail(20).std()
  
  # Generate 10 bid/ask levels around current price
  for i in range(10):
      bid_price = current_price × (1 - i × recent_volatility × 0.5)
      ask_price = current_price × (1 + i × recent_volatility × 0.5)
      
      bid_volume = random_based_on(recent_volume)
      ask_volume = random_based_on(recent_volume)
  ```
- **Note:** This is SYNTHETIC, not real NSE orderbook data
- **Purpose:** Shows buying/selling pressure based on volatility

---

### 5. **ORDERFLOW ABSORPTION**
**File:** `tradyxa_pipeline.py` → `generate_absorption_flow()` (Line 655)

**Data Source:**
- **Input:** Last 60 days of OHLCV data
- **Calculation:** Volume flow analysis
  ```python
  for each day:
      if Close > Open:
          Buy Flow += Volume × (Close - Open) / (High - Low)
          # More volume went up
      else:
          Sell Flow += Volume × (Open - Close) / (High - Low)
          # More volume went down
  ```
- **Shows:** Are buyers or sellers stronger over 60 days?
- **Interpretation:**
  - More green = institutional buying = potentially bullish
  - More red = institutional selling = potentially bearish

---

### 6. **ACTIVITY HEATMAP**
**File:** `tradyxa_pipeline.py` → `generate_heatmap()` (Line 691)

**Data Source:**
- **Input:** Last 60 days of OHLCV data
- **Grid Construction:**
  ```python
  168 cells = 24 hours × 7 days
  
  For each day in last 60 days:
      hour_index = time_of_day (0-23)
      day_index = day_of_week (0-6)
      cell[hour_index][day_index] += volume
  ```
- **Shows:** Busiest trading times
  - Darker color = more volume traded at that time
  - Typically busiest: Market open (9:15) and close (3:30)

---

### 7. **RETURNS DISTRIBUTION (Histogram)**
**File:** `tradyxa_pipeline.py` → `generate_histogram()` (Line 723)

**Data Source:**
- **Input:** Last 60 days of daily returns
- **Calculation:**
  ```python
  daily_returns = Close.pct_change() × 100  # Convert to percentage
  histogram_bins = 20  # Divide into 20 return ranges
  
  Count = how many days had return in each range
  Example: -2% to -1.5%: 3 days
           -1.5% to -1%: 5 days
           +1% to +1.5%: 4 days
  ```
- **Shows:** Price movement patterns
  - Narrow distribution = stable stock
  - Wide distribution = volatile stock

---

### 8. **SLIPPAGE VS VOLUME (Execution Expectation)**
**File:** `tradyxa_pipeline.py` → `generate_slippage_samples()` (Line 753)

**Data Source:**
- **Input:** Last 100 days of OHLCV data
- **Calculation:** 50 random samples showing execution costs
  ```python
  for each sample (50 times):
      pick_random_day = last 100 days
      volume_ratio = day_volume / average_volume
      
      base_slippage = 0.1%  # Minimum cost
      actual_slippage = base_slippage / (volume_ratio + 0.5)
      
      expected_price = Close
      actual_price = Close × (1 + slippage%)
  ```
- **Shows:** How much your order would "slip" (market impact) when:
  - Trading 1L (₹100,000)
  - Trading 2.5L (₹250,000)
  - Trading 5L (₹500,000)
  - Trading 10L (₹1,000,000)

---

### 9. **VERDICT** (Automated Trading Signal)
**File:** `tradyxa_pipeline.py` → `compute_verdict()` (Line 296)

**Data Sources:** Multi-factor analysis combining:

**A) Momentum** (45% weight)
```python
recent_return = (Close[today] / Close[5_days_ago]) - 1
momentum_score = recent_return / volatility
# Higher = stronger up move
```

**B) Flow/Absorption** (25% weight)
```python
coordinated_flow = net_buy_volume - net_sell_volume
flow_score = tanh(coordinated_flow / 2.0)
# Positive = more buying
```

**C) Liquidity** (15% weight)
```python
liquidity = (1 - market_fragmentation) × (1 - depth_cost)
# Higher = easier to trade
```

**D) Impact Cost/Slippage** (15% weight)
```python
slippage_median = median_execution_cost_from_50_samples
cost_score = -1 / (1 + exp(-(slippage × 4)))
# Negative if costs high
```

**Final Score Calculation:**
```python
SCORE = 0.45×Momentum + 0.25×Flow + 0.15×Liquidity + 0.15×Cost

if SCORE > 0.05:
    VERDICT = "UP" (Bullish)
elif SCORE < -0.05:
    VERDICT = "DOWN" (Bearish)
else:
    VERDICT = "NEUTRAL" (Sideways)
```

**Confidence:**
- Based on data quality (50+ samples needed)
- Component agreement (do all 4 factors agree?)
- Strength of signal

---

## 🔧 THE COMPLETE DATA FLOW

```
┌─────────────────────────────────────────────┐
│   Yahoo Finance (yfinance API)              │
│   Provides: 5-year OHLCV + current price   │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  data_manager.py                            │
│  - Caches CSV files locally                │
│  - Updates incrementally daily              │
│  - Stores: public/data/raw/{TICKER}.csv    │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  tradyxa_pipeline.py                        │
│  Reads CSV and generates:                  │
│  ├─ Volume Profile (60-day price buckets)  │
│  ├─ Candles (60 daily OHLC bars)           │
│  ├─ Bollinger Bands (20-day SMA ± 2σ)     │
│  ├─ Orderbook (synthetic around price)    │
│  ├─ Rolling Averages (MA5, MA20, MA50)    │
│  ├─ Absorption Flow (buy vs sell volume)  │
│  ├─ Heatmap (24h × 7d trading intensity) │
│  ├─ Histogram (returns distribution)      │
│  ├─ Slippage Samples (50 execution costs) │
│  └─ Verdict (AI-generated signal)          │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  JSON Output (1,458 files)                  │
│  public/data/ticker/{TICKER}.NS.json       │
│  Contains: All 9 tiles + metrics            │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  Express Server (server/routes.ts)          │
│  - Reads JSON files                         │
│  - Overlays LIVE spot price                │
│  - Updates every 30 seconds                │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  Frontend Dashboard (React)                 │
│  - Displays 9 tiles + verdict               │
│  - Shows LIVE spot price                   │
│  - Updates every 30 seconds                │
└─────────────────────────────────────────────┘
```

---

## ⚠️ IMPORTANT: CURRENT DATA ISSUE

**11 stocks have CORRUPTED data** (as of batch regeneration at 15:13:18):
```
HUDCO.NS:      Spot ₹232  but VP shows ₹232-37,900 (163.5x mismatch!)
SUZLON.NS:     Spot ₹53   but VP shows ₹53-4,619 (87.6x mismatch!)
OLAELEC.NS:    Spot ₹39   but VP shows ₹39-1,834 (46.9x mismatch!)
PVRINOX.NS:    Spot ₹1,137 but VP shows ₹1,093-45,744 (40.2x mismatch!)
ACE.NS:        Spot ₹972  but VP shows ₹971-31,495 (32.4x mismatch!)
PCBL.NS:       Spot ₹315  but VP shows ₹315-9,798 (31.1x mismatch!)
SONACOMS.NS:   Spot ₹496  but VP shows ₹496-14,909 (30.1x mismatch!)
MRPL.NS:       Spot ₹157  but VP shows ₹156-2,674 (17.1x mismatch!)
BAJFINANCE.NS: Spot ₹1,022 but VP shows ₹1,014-9,440 (9.2x mismatch!)
PPLPHARMA.NS:  Spot ₹184  but VP shows ₹183-1,567 (8.5x mismatch!)
KSB.NS:        Spot ₹745  but VP shows ₹739-4,452 (6.0x mismatch!)
```

**Root Cause:** Volume Profile pulling from ENTIRE historical range instead of last 60 days.

**Fix in Progress:** Batch regeneration running (started 15:13:18) will recalculate all 9 tiles with correct 60-day windows for all 503 stocks.

---

## 📈 SUMMARY TABLE

| Tile | Source | Window | Calculated | Real vs Synthetic |
|------|--------|--------|------------|------------------|
| Volume Profile | OHLCV | 60 days | Yes (price buckets) | Real |
| Candles | OHLCV | 60 days | No (direct) | Real |
| Bollinger Bands | Close | 80 days | Yes (20-SMA ±2σ) | Real |
| Orderbook | OHLCV | Last 20 days volatility | Yes (synthetic) | Synthetic |
| Rolling Averages | Close | 70 days | Yes (MA5/20/50) | Real |
| Absorption Flow | OHLCV | 60 days | Yes (buy/sell split) | Real |
| Activity Heatmap | OHLCV | 60 days | Yes (volume grid) | Real |
| Returns Histogram | Close | 60 days | Yes (return bins) | Real |
| Slippage Samples | OHLCV + Volume | 100 days (50 samples) | Yes (volume-based) | Real |
| **Verdict** | **All Above** | **Varies** | **Yes (ML scoring)** | **Synthetic** |

---

## 🔄 UPDATE FREQUENCY

- **OHLCV Data:** Updated daily via `data_manager.py`
- **JSON Tiles:** Regenerated in batch (~1-2x per week or on-demand)
- **Live Spot Price:** Updated every 30 minutes via `fetch_spot_prices.py`
- **Verdict:** Recalculated with each batch regeneration

---

## 🎓 KEY TAKEAWAY

**ALL 9 tiles are 100% derived from Yahoo Finance OHLCV data** - they're different analytical perspectives of the same underlying stock price/volume history, combined to give you a complete market microstructure view for informed trading decisions.
