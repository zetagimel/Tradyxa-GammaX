# BATCH REGENERATION COMMANDS - Complete Guide

## What the Batch Regeneration Does

The batch regeneration re-processes all 503 NIFTY stocks through the complete pipeline:

```
Fetch OHLCV from Cache (CSV) 
    ↓
Compute 9 Financial Features
    ↓
Generate 9 Market Tiles (Volume Profile, Candles, Bollinger, etc.)
    ↓
Calculate Verdict Signal
    ↓
Write JSON Files (3 files per stock: main + slippage + monte carlo)
```

**Total Output:** 1,509 files updated (503 stocks × 3 files each)

---

## 🚀 COMMAND TO RUN BATCH REGENERATION

### Basic Command (4 parallel workers)
```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx"

python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
```

### With Output Logging
```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx"

python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf 2>&1 | Tee-Object -FilePath batch_output.log
```

### With Background Execution (doesn't block terminal)
```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx"

Start-Process python -ArgumentList @(
    "scripts/tradyxa_pipeline.py",
    "--mode", "batch_run",
    "--tickers-file", "scripts/nifty500.txt",
    "--max-workers", "4",
    "--use-yf"
) -NoNewWindow -RedirectStandardOutput "batch_output.log" -RedirectStandardError "batch_errors.log"
```

---

## ⚙️ COMMAND BREAKDOWN

```
python scripts/tradyxa_pipeline.py
    ↓
    --mode batch_run
        Process all tickers from file (not single ticker)
    
    --tickers-file scripts/nifty500.txt
        File containing list of 503 tickers (one per line)
        Example lines:
        ^NSEI
        ^NSEBANK
        360ONE.NS
        3MINDIA.NS
        ...
        ZEALOUSTEEL.NS
    
    --max-workers 4
        Number of parallel threads
        Options: 1-8 (more = faster but uses more CPU)
        Default: 4
    
    --use-yf
        Fetch data from Yahoo Finance (default behavior)
        If omitted: uses cached CSV files only
```

---

## 🔧 ALTERNATIVE SINGLE-TICKER COMMANDS

### Regenerate Just ONE Ticker
```powershell
python scripts/tradyxa_pipeline.py --mode run_all --ticker NTPC.NS --use-yf
```

### Regenerate ONE Ticker with Synthetic Data (testing)
```powershell
python scripts/tradyxa_pipeline.py --mode sample_data --ticker NTPC.NS
```

---

## 📊 WHAT EACH COMMAND DOES

### `--mode batch_run`
- Reads all tickers from file
- Creates thread pool with `max_workers` threads
- Each thread processes one ticker completely (5-15 seconds)
- Shows progress bar: `50%|████▌     | 251/503 [2:15<2:16, 1.85s/it]`
- Writes 3 JSON files per ticker when done
- Final: ~1,509 JSON files updated

### `--mode run_all --ticker NTPC.NS`
- Processes SINGLE ticker completely
- Takes 5-15 seconds
- Writes 3 JSON files for NTPC
- Used for testing or targeted updates

### `--mode sample_data --ticker NTPC.NS`
- Generates synthetic OHLCV (not real Yahoo data)
- Used for testing without network calls
- Useful for debugging

---

## 📈 EXPECTED EXECUTION TIME

```
Batch Size: 503 stocks
Workers: 4 parallel threads
Time per stock: ~3 seconds

Estimated Total Time:
503 stocks ÷ 4 workers = ~126 batches
126 batches × 3 seconds = ~378 seconds = 6-7 minutes

Progress:
0% .......... 25% .......... 50% .......... 75% .......... 100%
[==========================================================] 100%
```

---

## 📁 FILES INVOLVED

### Input Files
```
scripts/tradyxa_pipeline.py         Main pipeline script (970 lines)
scripts/nifty500.txt                List of 503 tickers (one per line)
public/data/raw/*.csv               Cached OHLCV data (CSV format)
```

### Output Files (Generated/Updated)
```
public/data/ticker/{TICKER}.json                    Main market data (1,458 KB each)
public/data/ticker/{TICKER}_slippage.json           Slippage analysis
public/data/ticker/{TICKER}_monte_slippage.json     Monte Carlo slippage

Total: 1,509 files × 150 KB = ~225 MB
```

---

## 🔍 HOW TO MONITOR BATCH PROGRESS

### Option 1: Watch Live Output
```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx"

# Run with progress visible
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
```

### Option 2: Check File Modification Times
```powershell
# Show 5 most recently updated files
Get-ChildItem "public/data/ticker/*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | ForEach-Object { Write-Host "$($_.Name) - $($_.LastWriteTime.ToString('HH:mm:ss'))" }
```

### Option 3: Count Updated Files
```powershell
# Count files updated in last 5 minutes
(Get-ChildItem "public/data/ticker/*.json" | Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-5) } | Measure-Object).Count
```

### Option 4: Watch Progress Bar
```powershell
# Shows real-time progress with ETA
# Example output:
# 50%|████▌     | 251/503 [2:15<2:16, 1.85s/it]
#  ↑           ↑        ↑        ↑       ↑
# percentage  bar    done/total elapsed/remaining speed
```

---

## ⚡ OPTIMIZATION OPTIONS

### Faster Processing (8 Workers)
```powershell
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 8 --use-yf
```
- Uses more CPU
- Finishes in ~3-4 minutes instead of 6-7
- May cause system slowdown

### Slower but Less Resource Usage (2 Workers)
```powershell
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 2 --use-yf
```
- Gentle on system
- Takes ~12-14 minutes
- Good for background processing

### Use Cached Data Only (No Network)
```powershell
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4
```
- Omit `--use-yf` to skip Yahoo Finance calls
- Uses only cached CSV files
- Faster but may miss latest data

---

## 🐛 TROUBLESHOOTING COMMANDS

### Test Single Ticker First
```powershell
# Make sure it works before full batch
python scripts/tradyxa_pipeline.py --mode run_all --ticker NTPC.NS --use-yf
```

### Check Ticker File Format
```powershell
# Should show ~503 lines, one ticker per line
Get-Content scripts/nifty500.txt | Measure-Object -Line
```

### View Recent Errors
```powershell
# Show last 20 lines of log
Get-Content batch_output.log -Tail 20
```

### Kill Running Batch (if needed)
```powershell
# Find Python process
Get-Process python | Where-Object { $_.CommandLine -like "*tradyxa_pipeline*" }

# Kill specific process
Stop-Process -Id <PID>
```

---

## 📋 BATCH EXECUTION SEQUENCE (What Happens)

For each ticker in nifty500.txt:

```
1. Fetch OHLCV Data
   - Read CSV from public/data/raw/{TICKER}.csv
   - Or fetch from Yahoo Finance if --use-yf is set
   
2. Feature Engineering (compute_features_for_df)
   - Amihud liquidity measure
   - Lambda price impact coefficient
   - Market fragmentation coefficient (MFC)
   - Volume Z-score
   - Volatility (20-day rolling)
   - Coordinated flow (buy/sell imbalance)
   - Returns
   - High-Low-Close ratio
   - Time of day
   
3. Generate 9 Market Tiles
   - Volume Profile (60-day price distribution)
   - Candles (60 daily OHLC bars)
   - Bollinger Bands (20-SMA ± 2σ)
   - Orderbook (synthetic depth)
   - Rolling Averages (MA5, MA20, MA50)
   - Absorption Flow (buy vs sell volume)
   - Activity Heatmap (24h × 7d intensity)
   - Returns Histogram (20 bins)
   - Slippage Samples (50 execution costs)
   
4. Calculate Slippage Analysis
   - Deterministic slippage for 4 notional sizes
   - Monte Carlo slippage (400 simulations)
   
5. Generate Verdict Signal
   - Composite score: 45% momentum + 25% flow + 15% liquidity + 15% cost
   - Direction: UP / DOWN / NEUTRAL
   - Confidence score
   - Data quality rating
   
6. Write 3 JSON Files
   - {TICKER}.json (main file with all 9 tiles)
   - {TICKER}_slippage.json (slippage analysis)
   - {TICKER}_monte_slippage.json (Monte Carlo results)
```

---

## ✅ SUCCESS INDICATORS

After batch completes, check:

```powershell
# All file timestamps should be very recent
Get-Item "public/data/ticker/NTPC.NS.json" | Select-Object LastWriteTime

# Output:
# Wednesday, December 3, 2025 3:20:15 PM  ✓ Fresh!

# File size should be reasonable (~150-200 KB)
Get-Item "public/data/ticker/NTPC.NS.json" | Select-Object Length

# Output:
# 187432  ✓ Good size

# JSON should be valid (no parsing errors)
python -c "import json; json.load(open('public/data/ticker/NTPC.NS.json'))"
# No output = Success!
```

---

## 🎯 NEXT STEPS

1. **Run Batch:**
   ```powershell
   python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
   ```

2. **Wait for Completion** (6-7 minutes)

3. **Verify Results:**
   ```powershell
   Get-ChildItem "public/data/ticker/NTPC.NS.json" | Select-Object LastWriteTime
   ```

4. **Deploy to Production:**
   ```powershell
   git add public/data/ticker/
   git commit -m "Fix corrupted tile data - regenerate all 503 stocks"
   git push origin main
   ```

5. **Test in Frontend:**
   - Restart web server
   - Open dashboard
   - Verify tiles show correct price ranges
   - Verify verdict calculations

---

## 💡 WHAT IT FIXES

**Before Batch:**
```
NTPC spot: ₹322.05
Volume Profile: 2800-3400 (WRONG!)  ❌
Candles: 2800-3400 (WRONG!)  ❌
Verdict: NEUTRAL/WRONG  ❌
```

**After Batch:**
```
NTPC spot: ₹322.05
Volume Profile: ₹321-348 (60-day range)  ✓
Candles: ₹321-348 (60-day range)  ✓
Verdict: Correct calculation  ✓
All 503 stocks: Fresh data  ✓
```
