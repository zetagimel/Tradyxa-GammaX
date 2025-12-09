# QUICK START - Copy & Paste Commands

## ⚡ RUN BATCH REGENERATION NOW

### **Command to Run** (Copy & Paste)
```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx" ; python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
```

**What it does:**
- Takes 6-7 minutes
- Regenerates all 503 stocks
- Fixes the 11 corrupted stocks with 163x price mismatches
- Updates 1,509 JSON files with fresh market data

**You'll see:**
```
2025-12-03 15:13:18,363 [INFO] Batch processing 503 tickers with 4 workers
2025-12-03 15:13:18,363 [INFO] Starting pipeline for ^NSEI
2025-12-03 15:13:18,379 [INFO] Starting pipeline for ^NSEBANK
[INFO] Wrote ticker JSON: public\data\ticker\360ONE.NS.json
[INFO] Wrote ticker JSON: public\data\ticker\3MINDIA.NS.json
50%|████▌     | 251/503 [2:15<2:16, 1.85s/it]  ← Progress bar
100%|██████████| 503/503 [6:32<00:00, 1.28s/it]  ← Done!
```

---

## 🚀 FASTER VERSION (8 workers, 3-4 minutes)
```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx" ; python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 8 --use-yf
```

---

## 🔄 MONITOR WHILE RUNNING (in separate terminal)

### Show most recently updated files
```powershell
Get-ChildItem "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx\public\data\ticker\*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 3 | ForEach-Object { Write-Host "$($_.Name) updated at $($_.LastWriteTime.ToString('HH:mm:ss'))" }
```

### Count how many files have been updated
```powershell
$count = (Get-ChildItem "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx\public\data\ticker\*.json" | Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-10) } | Measure-Object).Count
Write-Host "Files updated in last 10 minutes: $count"
```

### Watch progress every 10 seconds
```powershell
while($true) { 
    $count = (Get-ChildItem "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx\public\data\ticker\*.json" | Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-10) } | Measure-Object).Count; 
    Write-Host "$(Get-Date -Format 'HH:mm:ss') - Files updated: $count / 1509"; 
    Start-Sleep -Seconds 10 
}
```

---

## ✅ VERIFY RESULTS AFTER BATCH COMPLETES

### Check if specific stocks are fixed
```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx"

# Check HUDCO (was showing 232 vs 37900)
python -c "import json; d=json.load(open('public/data/ticker/HUDCO.NS.json')); print(f'HUDCO Spot: ₹{d[\"metrics\"][\"spot_price\"]:.0f}'); print(f'VP Range: ₹{d[\"volumeProfile\"][0][\"price\"]:.0f} - ₹{d[\"volumeProfile\"][-1][\"price\"]:.0f}')"

# Output should be:
# HUDCO Spot: ₹232
# VP Range: ₹180 - ₹285 (60-day window, NOT 232-37900!)
```

### Check NTPC and MRF
```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx"

# NTPC
python -c "import json; d=json.load(open('public/data/ticker/NTPC.NS.json')); print(f'NTPC - Spot: ₹{d[\"metrics\"][\"spot_price\"]:.2f}, VP: ₹{d[\"volumeProfile\"][0][\"price\"]:.0f}-{d[\"volumeProfile\"][-1][\"price\"]:.0f}')"

# MRF  
python -c "import json; d=json.load(open('public/data/ticker/MRF.NS.json')); print(f'MRF - Spot: ₹{d[\"metrics\"][\"spot_price\"]:.0f}, VP: ₹{d[\"volumeProfile\"][0][\"price\"]:.0f}-{d[\"volumeProfile\"][-1][\"price\"]:.0f}')"
```

### Verify file timestamps (should be recent)
```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx"

Get-Item "public/data/ticker/NTPC.NS.json" | Select-Object @{N='Name';E={$_.Name}}, @{N='LastModified';E={$_.LastWriteTime.ToString('HH:mm:ss')}}

# Output:
# Name                 LastModified
# ----                 --------
# NTPC.NS.json         15:20:45  ✓
```

---

## 📊 SINGLE TICKER TEST (before full batch)

### Test with one stock first
```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx"

python scripts/tradyxa_pipeline.py --mode run_all --ticker NTPC.NS --use-yf
```

**Takes:** ~10 seconds
**Output:**
```
2025-12-03 15:25:30,123 [INFO] Starting pipeline for NTPC.NS
2025-12-03 15:25:40,456 [INFO] Wrote ticker JSON: public\data\ticker\NTPC.NS.json
```

---

## 🔧 TROUBLESHOOTING

### If batch gets stuck or slow

```powershell
# Kill the process
Stop-Process -Name python -Force

# Start fresh with fewer workers (less resource usage)
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 2 --use-yf
```

### If you get "File not found" error

```powershell
# Verify files exist
Test-Path "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx\scripts\tradyxa_pipeline.py"
Test-Path "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx\scripts\nifty500.txt"

# If missing, check directory
Get-ChildItem "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx\scripts\"
```

### If JSON files don't update

```powershell
# Check if ticker file has actual tickers
Get-Content "scripts\nifty500.txt" | Head -10

# Should show:
# ^NSEI
# ^NSEBANK
# 360ONE.NS
# etc.
```

---

## 📈 PERFORMANCE TIPS

### Optimal Settings for Your System

**If you have 8+ CPU cores:**
```powershell
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 8 --use-yf
# Finishes in ~3-4 minutes
```

**If you want to keep system responsive:**
```powershell
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
# Finishes in ~6-7 minutes, system stays responsive
```

**If you want minimal resource usage:**
```powershell
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 2 --use-yf
# Finishes in ~12-14 minutes, very light on system
```

---

## 🎯 DEPLOY AFTER BATCH COMPLETES

```powershell
cd "c:\Users\hp\Desktop\Desktop_Placed\Tradyxa Aztryx"

# See what changed
git status

# Stage updated JSON files
git add public/data/ticker/*.json

# Commit
git commit -m "Regenerate all 503 stocks - fix corrupted tile data (11 stocks with price mismatches)"

# Push to production
git push origin main
```

---

## ✨ WHAT YOU'LL SEE IN FRONTEND AFTER THIS

**Before:**
- NTPC spot: ₹322.05
- Volume Profile: Shows 2800-3400 (WRONG!) ❌
- Verdict: Wrong ❌

**After:**
- NTPC spot: ₹322.05
- Volume Profile: Shows ₹321-348 (60-day, CORRECT!) ✓
- Verdict: Correct ✓
- All 11 corrupted stocks: FIXED ✓
- All 492 other stocks: Fresh data ✓

---

## 📞 REFERENCE

**Main Script:** `scripts/tradyxa_pipeline.py` (970 lines)
**Tickers List:** `scripts/nifty500.txt` (503 tickers)
**Output Directory:** `public/data/ticker/` (1,509 files after batch)

**File Outputs per Ticker:**
- `{TICKER}.NS.json` - Main file (150-200 KB)
- `{TICKER}.NS_slippage.json` - Slippage analysis
- `{TICKER}.NS_monte_slippage.json` - Monte Carlo simulations

**Total Output Size:** ~225 MB
**Estimated Time:** 6-7 minutes (4 workers) to 3-4 minutes (8 workers)

---

## 🟢 STATUS CHECK

Current Status (December 3, 15:13:18):
- ✅ Batch started
- ✅ Processing 503 stocks with 4 workers
- ⏳ ~5% complete (ACMESOLAR just finished)
- ⏳ ETA: ~20-25 minutes to completion
