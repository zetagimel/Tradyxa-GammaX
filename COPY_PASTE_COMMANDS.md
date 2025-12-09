# EXACT COMMANDS - Complete Daily Schedule

## 📅 DAILY COMMAND SCHEDULE

### All Commands You Should Run & When

---

## 🎯 COMMAND #1: UPDATE LIVE SPOT PRICES
**Purpose:** Fetch current spot prices (updates frontend prices in real-time)  
**Frequency:** **3-4 times per day** (every ~6-8 hours)  
**Duration:** 3-5 minutes  
**When:** Morning, Afternoon, Evening (market open, mid-day, market close)

```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx" ; python scripts/fetch_spot_prices.py
```

**What it does:**
- Fetches current spot price for all 503 stocks
- Gets India VIX index
- Updates `public/data/live/spot_prices.json`
- Used by frontend for live price display

**Expected output:**
```
Fetching spot prices for 503 tickers...
NTPC.NS: ₹322.05
TCS.NS: ₹4,250.30
... (501 more stocks)
✅ Saved live spot prices to public/data/live/spot_prices.json
India VIX: 11.19
Updated 503 tickers at 15:48:22
```

---

## 🎯 COMMAND #2: REGENERATE ALL TILES & VERDICTS
**Purpose:** Regenerate market tiles (Volume Profile, Candles, etc.) and verdicts  
**Frequency:** **1-2 times per day** (daily or every other day)  
**Duration:** 6-7 minutes  
**When:** Evening (after market close, ~4:00 PM) or early morning

```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx" ; python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
```

**What it does:**
- Regenerates all 9 market tiles for 503 stocks
- Recalculates verdicts (BUY/SELL/HOLD signals)
- Updates slippage expectations
- Generates 1,509 JSON files
- Fixes corrupted data

**Expected output:**
```
2025-12-03 16:00:00,000 [INFO] Batch processing 503 tickers with 4 workers
100%|██████████| 503/503 [6:32<00:00, 1.28s/it]
All 503 stocks regenerated ✓
```

---

## 🎯 COMMAND #3: REGENERATE SINGLE TICKER (Testing)
**Purpose:** Test or regenerate one specific stock  
**Frequency:** **As needed** (for testing/troubleshooting)  
**Duration:** 10-15 seconds  
**When:** Anytime (for verification)

```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx" ; python scripts/tradyxa_pipeline.py --mode run_all --ticker NTPC.NS --use-yf
```

**Example with different stocks:**
```powershell
# Test with NTPC
python scripts/tradyxa_pipeline.py --mode run_all --ticker NTPC.NS --use-yf

# Test with MRF
python scripts/tradyxa_pipeline.py --mode run_all --ticker MRF.NS --use-yf

# Test with HDFC
python scripts/tradyxa_pipeline.py --mode run_all --ticker HDFC.NS --use-yf
```

**What it does:**
- Processes one ticker completely
- Generates 3 JSON files for that ticker
- Takes ~10-15 seconds
- Useful for debugging

---

## 🎯 COMMAND #4: UPDATE OHLCV DATA FROM YAHOO
**Purpose:** Fetch latest historical data (5-year OHLCV)  
**Frequency:** **Once per day** (daily, after market close)  
**Duration:** Variable (depends on internet)  
**When:** Evening (after market close)

```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx" ; python scripts/data_manager.py --mode update_all
```

**What it does:**
- Updates CSV files with latest OHLCV data from Yahoo Finance
- Incremental update (only new data, faster)
- Caches to `public/data/raw/{TICKER}.csv`
- Required before running batch regeneration

**Expected output:**
```
Updating OHLCV data for 503 stocks...
NTPC.NS: Updated (1,240 bars)
TCS.NS: Updated (1,240 bars)
... (501 more)
✅ All 503 stocks updated
```

---

## 🎯 COMMAND #5: APPLY ML MODELS
**Purpose:** Apply trained ML models (regime classifier, slippage predictor)  
**Frequency:** **1-2 times per day** (after batch regeneration)  
**Duration:** 5-10 minutes  
**When:** After running batch regeneration

```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx" ; python scripts/apply_models.py --mode batch
```

**What it does:**
- Applies Random Forest regime classifier
- Applies Quantile Regression slippage predictor
- Adds ML predictions to JSON files
- Enhances verdict calculation

**Expected output:**
```
Applying ML models to 503 stocks...
Processing NTPC.NS... ✓
Processing TCS.NS... ✓
... (501 more)
✅ ML models applied to all 503 stocks
```

---

## 🎯 COMMAND #6: DEPLOY TO PRODUCTION
**Purpose:** Push updated files to git repository  
**Frequency:** **Once per day** (after all regenerations complete)  
**Duration:** 1-2 minutes  
**When:** Evening (after batch + ML models complete)

```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx"

# Stage all updated files
git add public/data/ticker/*.json
git add public/data/live/spot_prices.json

# Commit with message
git commit -m "Daily regeneration: update tiles, verdicts, and spot prices - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"

# Push to production
git push origin main
```

**What it does:**
- Stages updated JSON and price files
- Creates commit with timestamp
- Pushes to main branch
- Frontend automatically picks up changes

**Expected output:**
```
[main 3f4a8b2] Daily regeneration: update tiles, verdicts, and spot prices
 1509 files changed, 234567 insertions(+), 234567 deletions(-)
 100% (1509/1509) processing
Enumerating objects: 1509, done.
✅ Pushed to origin main
```

---

## 📊 COMPLETE DAILY SCHEDULE (Recommended)

```
┌─────────────────────────────────────────────────────────────────┐
│  MORNING (9:15 AM - Market Open)                               │
├─────────────────────────────────────────────────────────────────┤
│  1. Update Spot Prices (Command #1) - 3-5 min                  │
│     python scripts/fetch_spot_prices.py                        │
│                                                                 │
│     Why: Get fresh prices at market open                       │
│     Impact: Frontend shows current prices                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  AFTERNOON (1:00 PM - Mid-day)                                 │
├─────────────────────────────────────────────────────────────────┤
│  2. Update Spot Prices (Command #1) - 3-5 min                  │
│     python scripts/fetch_spot_prices.py                        │
│                                                                 │
│     Why: Update mid-day prices                                 │
│     Impact: Frontend prices stay current                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  EVENING (4:00 PM - Market Close)                              │
├─────────────────────────────────────────────────────────────────┤
│  SEQUENCE:                                                      │
│                                                                 │
│  3. Update Spot Prices (Command #1) - 3-5 min                  │
│     python scripts/fetch_spot_prices.py                        │
│                                                                 │
│  4. Update OHLCV Data (Command #4) - 5-10 min                  │
│     python scripts/data_manager.py --mode update_all           │
│                                                                 │
│  5. Batch Regeneration (Command #2) - 6-7 min                  │
│     python scripts/tradyxa_pipeline.py --mode batch_run ...    │
│                                                                 │
│  6. Apply ML Models (Command #5) - 5-10 min                    │
│     python scripts/apply_models.py --mode batch                │
│                                                                 │
│  7. Deploy to Git (Command #6) - 1-2 min                       │
│     git add . ; git commit -m "..." ; git push                 │
│                                                                 │
│  Total Evening Time: ~20-35 minutes                            │
│  Why: All fresh data + models + deployment                    │
│  Impact: Production has latest everything                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⏱️ FREQUENCY SUMMARY TABLE

| Command | Purpose | Frequency | Duration | Best Time |
|---------|---------|-----------|----------|-----------|
| **#1: Spot Prices** | Live frontend prices | 3-4x/day | 3-5 min | 9:15 AM, 1:00 PM, 3:50 PM |
| **#2: Batch Regen** | All tiles + verdicts | 1-2x/day | 6-7 min | 4:00 PM (after close) |
| **#3: Single Ticker** | Test/debug | As needed | 10-15 sec | Anytime |
| **#4: OHLCV Update** | Historical data | 1x/day | 5-10 min | 4:00 PM (before batch) |
| **#5: ML Models** | Predictions | 1-2x/day | 5-10 min | 4:10 PM (after batch) |
| **#6: Git Deploy** | Push to production | 1x/day | 1-2 min | 4:20 PM (after all) |

---

## 🚀 QUICK START SEQUENCE (Complete Full Cycle)

Run these commands in order, one after another:

```powershell
# Step 1: Update Spot Prices (3-5 min)
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx"
python scripts/fetch_spot_prices.py

# Step 2: Update Historical Data (5-10 min)
python scripts/data_manager.py --mode update_all

# Step 3: Regenerate All Tiles (6-7 min)
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf

# Step 4: Apply ML Models (5-10 min)
python scripts/apply_models.py --mode batch

# Step 5: Deploy to Production (1-2 min)
git add public/data/
git commit -m "Daily regeneration: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git push origin main
```

**Total Time: ~20-35 minutes**  
**Result: Completely fresh data in production**

---

## 📋 COMMAND REFERENCE BY PURPOSE

### To Update Frontend Prices Only
```powershell
python scripts/fetch_spot_prices.py
```
Run: 3-4 times daily  

### To Regenerate All Market Tiles
```powershell
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
```
Run: 1-2 times daily

### To Test Single Stock
```powershell
python scripts/tradyxa_pipeline.py --mode run_all --ticker NTPC.NS --use-yf
```
Run: As needed

### To Update Historical Data
```powershell
python scripts/data_manager.py --mode update_all
```
Run: Once daily

### To Apply ML Predictions
```powershell
python scripts/apply_models.py --mode batch
```
Run: After batch regeneration

### To Deploy Everything
```powershell
git add public/data/ ; git commit -m "Daily update" ; git push origin main
```
Run: Once daily

---

## ✅ THE ONE COMMAND YOU NEED (for basic usage)

If you only have time for ONE command, run this (regenerates all tiles):

```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx" ; python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
```

That's it! Let it run for 6-7 minutes.
---

## 🎬 WHAT YOU'LL SEE (Step by Step)

### Second 0-5: Startup
```
PS C:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx> python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
2025-12-03 15:13:18,363 [INFO] Batch processing 503 tickers with 4 workers
2025-12-03 15:13:18,363 [INFO] Starting pipeline for ^NSEI
2025-12-03 15:13:18,379 [INFO] Starting pipeline for ^NSEBANK
2025-12-03 15:13:18,379 [INFO] Starting pipeline for 360ONE.NS
2025-12-03 15:13:18,379 [INFO] Starting pipeline for 3MINDIA.NS
```

### Second 5-20: Processing starts
```
2025-12-03 15:13:18,410 [INFO] ^NSEI is up to date (Last: 2025-12-03)
2025-12-03 15:13:18,457 [INFO] 3MINDIA.NS is up to date (Last: 2025-12-03)
2025-12-03 15:13:18,473 [INFO] 360ONE.NS is up to date (Last: 2025-12-03)
2025-12-03 15:13:18,610 [INFO] ^NSEBANK is up to date (Last: 2025-12-03)

FutureWarning: Series.fillna with 'method' is deprecated and will raise in a future version. Use obj.ffill() or obj.bfill() instead.
  vol = df_ohlcv["Volume"].replace(0, np.nan).fillna(method='ffill').fillna(1.0)

2025-12-03 15:13:34,081 [INFO] Wrote ticker JSON: public\data\ticker\360ONE.NS.json
2025-12-03 15:13:34,154 [INFO] Wrote ticker JSON: public\data\ticker\^NSEI.json
```

### Second 20-60: Progress bar appears
```
  1%|          | 5/503 [00:21<24:06, 2.90s/it]
  
  ↑           ↑         ↑        ↑       ↑
percentage  bar    completed/total  elapsed  rate
```

### Second 60-120: Halfway point
```
 50%|████▌     | 251/503 [2:15<2:16, 1.85s/it]
```

### Second 360-400: Finishing
```
 98%|█████████▊| 495/503 [6:25<00:08, 0.98s/it]
```

### Second 400: Done!
```
100%|██████████| 503/503 [6:32<00:00, 1.28s/it]

PS C:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx>
```

---

## 🎯 WHAT THE PROGRESS BAR MEANS

```
 50%|████▌     | 251/503 [2:15<2:16, 1.85s/it]
 ↑   ↑         ↑   ↑     ↑      ↑      ↑
 |   |         |   |     |      |      └─ Speed: 1.85 seconds per stock
 |   |         |   |     |      └──────── Remaining time: 2:16 (2 min 16 sec)
 |   |         |   |     └─────────────── Elapsed: 2:15 (2 min 15 sec)
 |   |         |   └───────────────────── Total to process: 503 stocks
 |   |         └───────────────────────── Completed: 251 stocks
 |   └───────────────────────────────── Progress bar (filled)
 └───────────────────────────────────── Percentage: 50% done
```

**Example Predictions:**
```
If at 2 minutes you see: 50/503 [2:00<25:00, 1.80s/it]
→ Remaining: 25 minutes, Total: ~27 minutes

If at 2 minutes you see: 100/503 [2:00<10:00, 1.20s/it]
→ Remaining: 10 minutes, Total: ~12 minutes

If at 2 minutes you see: 80/503 [2:00<12:00, 1.50s/it]
→ Remaining: 12 minutes, Total: ~14 minutes
```

---

## 📋 DURING EXECUTION - MONITORING (in separate terminal)

### Check Progress
```powershell
# Show last 3 modified files
Get-ChildItem "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx\public\data\ticker\*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 3 | ForEach-Object { "$($_.Name) - $($_.LastWriteTime.ToString('HH:mm:ss'))" }
```

Expected output (changes as batch runs):
```
ACMESOLAR.NS_monte_slippage.json - 15:13:39
ACMESOLAR.NS_slippage.json - 15:13:39
ACMESOLAR.NS.json - 15:13:39
```

### Count Total Updated Files
```powershell
$start = (Get-Date).AddMinutes(-10)
$count = @(Get-ChildItem "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx\public\data\ticker\*.json" | Where-Object { $_.LastWriteTime -gt $start }).Count
"$count files updated in last 10 minutes"
```

Expected output (progresses as batch runs):
```
42 files updated in last 10 minutes
95 files updated in last 10 minutes
201 files updated in last 10 minutes
... continues until batch finishes
```

---

## ✅ AFTER EXECUTION - VERIFICATION

### Verify Batch Completed Successfully
```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx"

# Check if files are fresh (should show current time)
(Get-Item "public\data\ticker\NTPC.NS.json").LastWriteTime
(Get-Item "public\data\ticker\MRF.NS.json").LastWriteTime
(Get-Item "public\data\ticker\HUDCO.NS.json").LastWriteTime

# All three should show the time batch finished (e.g., 15:20:15)
```

### Verify Corruption is Fixed

```powershell
# Check NTPC (should be ~321-348 range, NOT 2800-3400)
python -c "
import json
d = json.load(open('public/data/ticker/NTPC.NS.json'))
print(f'NTPC:')
print(f'  Spot: ₹{d[\"metrics\"][\"spot_price\"]:.2f}')
print(f'  VP Range: ₹{d[\"volumeProfile\"][0][\"price\"]:.0f} - ₹{d[\"volumeProfile\"][-1][\"price\"]:.0f}')
print(f'  Status: {\"✓ CORRECT\" if d[\"volumeProfile\"][-1][\"price\"] < 400 else \"✗ STILL WRONG\"}')"
```

Expected output:
```
NTPC:
  Spot: ₹322.05
  VP Range: ₹321 - ₹348
  Status: ✓ CORRECT
```

### Verify the 11 Corrupted Stocks are Fixed

```powershell
$corrupted = @("HUDCO.NS", "SUZLON.NS", "OLAELEC.NS", "PVRINOX.NS", "ACE.NS", "PCBL.NS", "SONACOMS.NS", "MRPL.NS", "BAJFINANCE.NS", "PPLPHARMA.NS", "KSB.NS")

foreach ($ticker in $corrupted) {
    python -c "
import json
try:
    d = json.load(open('public/data/ticker/$ticker.json'))
    spot = d['metrics']['spot_price']
    vp_high = d['volumeProfile'][-1]['price']
    ratio = vp_high / spot if spot > 0 else 0
    status = '✓ FIXED' if ratio < 2 else '✗ STILL WRONG'
    print(f'$ticker: {status} (Ratio: {ratio:.1f}x)')
except:
    print(f'$ticker: ERROR')
" 2>/dev/null
}
```

Expected output:
```
HUDCO.NS: ✓ FIXED (Ratio: 1.2x)
SUZLON.NS: ✓ FIXED (Ratio: 1.1x)
OLAELEC.NS: ✓ FIXED (Ratio: 1.3x)
PVRINOX.NS: ✓ FIXED (Ratio: 1.5x)
ACE.NS: ✓ FIXED (Ratio: 1.2x)
PCBL.NS: ✓ FIXED (Ratio: 1.1x)
SONACOMS.NS: ✓ FIXED (Ratio: 1.2x)
MRPL.NS: ✓ FIXED (Ratio: 1.4x)
BAJFINANCE.NS: ✓ FIXED (Ratio: 1.3x)
PPLPHARMA.NS: ✓ FIXED (Ratio: 1.2x)
KSB.NS: ✓ FIXED (Ratio: 1.1x)
```

### Count Total Files Updated
```powershell
$all_files = Get-ChildItem "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx\public\data\ticker\*.json" | Measure-Object
"Total JSON files: $($all_files.Count)"

# Should be exactly 1,509 (503 stocks × 3 files)
```

Expected output:
```
Total JSON files: 1509
```

---

## 🚀 AFTER VERIFICATION - DEPLOY

```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx"

# See what changed
git status

# Add all updated JSON files
git add public/data/ticker/*.json

# Commit with message
git commit -m "Batch regeneration: fix corrupted tile data for all 503 stocks

- Fixed 11 corrupted stocks showing 5-163x price mismatches
- HUDCO, SUZLON, OLAELEC, PVRINOX, ACE, PCBL, SONACOMS, MRPL, BAJFINANCE, PPLPHARMA, KSB
- All tiles now show correct 60-day price ranges
- Regenerated verdicts with fresh market data
- 1,509 JSON files updated"

# Push to production
git push origin main
```

---

## 🐛 IF SOMETHING GOES WRONG

### Error: "File not found"
```powershell
# Make sure you're in correct directory
pwd  # Should show: C:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx

# Navigate there
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx"
```

### Error: "Python not found"
```powershell
# Check Python is installed
python --version

# If not in PATH, use full path
C:\Python311\python.exe scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
```

### Error: "nifty500.txt not found"
```powershell
# Check file exists
Test-Path "scripts\nifty500.txt"

# List what's in scripts folder
Get-ChildItem "scripts\"
```

### Batch Too Slow (stuck at 1%)
```powershell
# Try with fewer workers (less CPU usage)
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 2 --use-yf

# Or with network disabled (use cached CSVs only)
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4
```

### Want to Cancel
```powershell
# Press: Ctrl+C in the terminal running batch

# Or in another terminal:
Stop-Process -Name python -Force
```

---

## ✨ SUCCESS CHECKLIST

- [ ] Command executed without errors
- [ ] Progress bar showed 100%
- [ ] Terminal returned to prompt
- [ ] Files show recent timestamp (e.g., 15:20:45)
- [ ] HUDCO volume profile is now ~1.2x spot (not 163x)
- [ ] NTPC volume profile is now ~1.1x spot (not 2800-3400 range)
- [ ] All 1,509 files updated
- [ ] Ready to deploy to production

---

## 📊 EXPECTED TIMELINE

```
15:13:18 - START (run command)
15:13:20 - Reading tickers...
15:13:25 - First 4 workers start
15:15:00 - ~50 stocks done (10%)
15:16:30 - ~100 stocks done (20%)
15:17:45 - ~150 stocks done (30%)
15:19:00 - ~250 stocks done (50%)
15:20:15 - ~350 stocks done (70%)
15:21:30 - ~450 stocks done (90%)
15:22:45 - COMPLETE (100%)

Total time: ~9 minutes 27 seconds
```

(May vary ±1-2 minutes depending on your system/network)

---

## 🎓 KEY PARAMETERS EXPLAINED

```
--mode batch_run          ← Process all 503 (vs. single ticker)
--max-workers 4           ← 4 parallel threads (4x speed-up vs. 1)
--use-yf                  ← Fetch fresh from Yahoo (vs. cached only)
--tickers-file nifty500.txt ← List of stocks to process
```

To customize:
```
# Faster (8 workers, ~3.5 minutes)
--max-workers 8

# Slower but lighter (2 workers, ~12 minutes)
--max-workers 2

# Use cached CSVs only (skip Yahoo, ~20% faster)
(omit --use-yf)

# Single ticker test
--mode run_all --ticker NTPC.NS --use-yf
```

---

## 🎯 YOU'RE DONE WHEN:

```
PS C:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx> 
```

You're back at the prompt, batch finished successfully!
