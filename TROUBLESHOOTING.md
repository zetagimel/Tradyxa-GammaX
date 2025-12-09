# 🔧 Troubleshooting Guide

## Issue 1: 404 Errors - Ticker Symbols Missing `.NS` Suffix

### Problem
When running `fetch_spot_prices.py` or `tradyxa_pipeline.py`, you see errors like:
```
HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: AAVAS"}}}
```

### Root Cause
The ticker symbols in `scripts/nifty500.txt` were missing the `.NS` suffix required by yfinance for NSE stocks.

**Wrong:** `AAVAS`  
**Correct:** `AAVAS.NS`

### ✅ Solution - FIXED!
Run the ticker fetcher again to regenerate the file with correct `.NS` suffixes:

```bash
python scripts/fetch_tickers.py
```

This creates `scripts/nifty500.txt` with properly formatted tickers like:
- `AAVAS.NS`
- `ABCAPITAL.NS`
- `RELIANCE.NS`
- etc.

**The file has been regenerated successfully!** ✅

Now your data fetching scripts will work correctly.

---

## Issue 2: Git Push Stuck with HTTPS

### Problem
When trying to push via HTTPS, the command gets stuck at:
```
Writing objects: 10% (611/5671), 52.04 MiB | 488.00 KiB/s
```

### Root Cause
- Large repository size (~50-90 MB due to git history)
- Slow internet connection
- HTTPS connection timeout issues

### ✅ Solution - Switched to SSH!

The remote has been changed from HTTPS to SSH:

```bash
# Old (HTTPS)
origin  https://github.com/pravindev666/Gammax.git

# New (SSH) ✅
origin  git@github.com:pravindev666/Gammax.git
```

**Command used:**
```bash
git remote set-url origin git@github.com:pravindev666/Gammax.git
```

---

## How to Push via SSH

### Step 1: Verify SSH Keys Exist

```bash
ls ~/.ssh/
```

Should show:
- `id_rsa` (private key)
- `id_rsa.pub` (public key)

If they don't exist, generate them:
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

---

### Step 2: Add SSH Key to GitHub

1. Copy your public key:
   ```bash
   cat ~/.ssh/id_rsa.pub
   ```

2. Go to GitHub → **Settings** → **SSH and GPG keys** → **New SSH key**

3. Paste the public key and save

---

### Step 3: Test SSH Connection

```bash
ssh -T git@github.com
```

Should see:
```
Hi pravindev666! You've successfully authenticated...
```

---

### Step 4: Push via SSH

```bash
git push origin main
```

Or force push if needed:
```bash
git push -f origin main
```

**SSH is much faster and more reliable than HTTPS!** ✅

---

## Quick Reference

### Check Current Remote
```bash
git remote -v
```

### Switch to HTTPS
```bash
git remote set-url origin https://github.com/pravindev666/Gammax.git
```

### Switch to SSH
```bash
git remote set-url origin git@github.com:pravindev666/Gammax.git
```

---

## Summary of Fixes

| Issue | Status | Solution |
|-------|--------|----------|
| 404 errors for tickers | ✅ FIXED | Regenerated `nifty500.txt` with `.NS` suffixes |
| Git push stuck with HTTPS | ✅ FIXED | Switched to SSH remote |

---

## Next Steps

### 1. Retry Data Fetching
Now that ticker symbols are fixed:

```bash
# Fetch live prices (will work now!)
python scripts/fetch_spot_prices.py

# Or run bulk processing
python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
```

### 2. Push to GitHub via SSH
```bash
git add .
git commit -m "Fixed ticker symbols and switched to SSH"
git push origin main
```

---

## 🎯 Both Issues Resolved!

✅ Ticker symbols now have `.NS` suffix  
✅ Git remote switched to SSH for faster, more reliable pushes

You're good to go! 🚀
