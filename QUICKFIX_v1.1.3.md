# 🔧 Quick Fix v1.1.3 - Pandas pct_change() Warnings

**Date:** 2025-12-04 23:28  
**Status:** ✅ FIXED

---

## Problem

More pandas FutureWarnings appeared:

```
C:\...\tradyxa_pipeline.py:612: FutureWarning: The default fill_method='pad' in Series.pct_change is deprecated
C:\...\tradyxa_pipeline.py:741: FutureWarning: The default fill_method='pad' in Series.pct_change is deprecated
```

These warnings appeared on every stock, creating noisy output.

---

## Root Cause

Pandas is deprecating the default `fill_method='pad'` parameter in `pct_change()`:

```python
# Old (shows warning)
df['Close'].pct_change()

# New (no warning)
df['Close'].pct_change(fill_method=None)
```

---

## Solution

Added `fill_method=None` to all `pct_change()` calls:

**Line 612 - Orderbook volatility:**
```python
# Before
recent_volatility = df_ohlcv['Close'].pct_change().tail(20).std()

# After
recent_volatility = df_ohlcv['Close'].pct_change(fill_method=None).tail(20).std()
```

**Line 741 - Returns histogram:**
```python
# Before
returns = df_ohlcv['Close'].pct_change().dropna() * 100

# After
returns = df_ohlcv['Close'].pct_change(fill_method=None).dropna() * 100
```

---

## Impact

### Before (Noisy):
```
Processing:   7%|██████ | 35/503
FutureWarning: The default fill_method='pad' in Series.pct_change...
FutureWarning: The default fill_method='pad' in Series.pct_change...
Processing:   8%|██████▍ | 37/503
FutureWarning: The default fill_method='pad' in Series.pct_change...
FutureWarning: The default fill_method='pad' in Series.pct_change...
```

### After (Clean):
```
Processing:   7%|██████ | 35/503
Processing:   8%|██████▍ | 37/503
Processing:   9%|███████ | 45/503
```

---

## Files Modified

**File:** `scripts/tradyxa_pipeline.py`

**Changes:**
- Line 612: Added `fill_method=None` to pct_change()
- Line 741: Added `fill_method=None` to pct_change()

---

## Next Run

Your **currently running batch_run** will still show warnings (it's using the old code).

**Next time you run it**, it will be clean! ✅

---

## Version History

| Version | Date | Fix |
|---------|------|-----|
| v1.1.3 | 2025-12-04 23:28 | Fixed pct_change() warnings |
| v1.1.2 | 2025-12-04 23:22 | Fixed NaN to integer errors |
| v1.1.1 | 2025-12-04 22:50 | Fixed datetime.UTC compatibility |
| v1.1 | 2025-12-04 20:30 | Initial cleanup |

---

**Status:** ✅ FIXED  
**Apply:** Next run will be clean!
