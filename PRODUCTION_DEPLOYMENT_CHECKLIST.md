# ✅ Production Deployment Checklist

## Phase 1: Verification (Before Pushing to GitHub)

- [ ] **Verify all 1,458 JSON files exist**
  ```bash
  ls public/data/ticker/*.json | wc -l  # Should show ~1,458
  ```

- [ ] **Verify all 503 CSV files exist**
  ```bash
  ls public/data/raw/*.csv | wc -l  # Should show ~503
  ```

- [ ] **Verify all 3 models exist**
  ```bash
  ls models/*.joblib  # Should show 3 files
  ls models/*.json    # Should show 1 metadata file
  ```

- [ ] **Verify nifty500.txt has 503 tickers**
  ```bash
  wc -l scripts/nifty500.txt  # Should show 503 or 505 (with indices)
  ```

- [ ] **Spot check a few JSON files**
  ```bash
  python -c "import json; data=json.load(open('public/data/ticker/RELIANCE.NS.json')); print(f'Spot: {data[\"metrics\"][\"spot_price\"]}, Verdict: {data.get(\"verdict\", \"N/A\")}, Regime: {data.get(\"regime\", \"N/A\")}')"
  ```

- [ ] **Verify at least one CSV file has data**
  ```bash
  head public/data/raw/RELIANCE.NS.csv | wc -l  # Should show header + data rows
  ```

---

## Phase 2: GitHub Setup

- [ ] **Create/update `.github/workflows/live_spot_prices.yml`**
  - Runs: Every 30 min (3:45 AM - 10:00 AM UTC)
  - Script: `fetch_spot_prices.py`
  - Output: `public/data/live/spot_prices.json`

- [ ] **Create/update `.github/workflows/daily_update.yml`**
  - Runs: Daily 10:15 AM UTC (3:45 PM IST) on weekdays
  - Scripts: `tradyxa_pipeline.py (--max-workers 2)` + `apply_models.py`
  - Output: `public/data/ticker/*.json` + `public/data/raw/*.csv`

- [ ] **Create/update `.github/workflows/train.yml`**
  - Runs: Weekly Sunday midnight UTC
  - Scripts: `tradyxa_pipeline.py (--max-workers 4)` + training + `apply_models.py`
  - Output: `models/*.joblib` + updated JSONs

- [ ] **Commit all workflow files**
  ```bash
  git add .github/workflows/
  git commit -m "Add production GitHub Actions workflows"
  ```

- [ ] **Push to GitHub**
  ```bash
  git push
  ```

- [ ] **Verify workflows appear in GitHub**
  - Go to: GitHub Repo → Actions → Should show 3 workflows

---

## Phase 3: Data Commit

- [ ] **Commit all generated data**
  ```bash
  git add public/data/ticker/*.json
  git add public/data/raw/*.csv
  git add models/*.joblib
  git add models/*.json
  git commit -m "chore: production data - all 503 stocks with real data"
  git push
  ```

- [ ] **Verify files on GitHub**
  - Check: All 1,458 JSON files visible in repo
  - Check: All models accessible

---

## Phase 4: Cloudflare Pages Setup

- [ ] **Connect GitHub repo to Cloudflare Pages**
  - Cloudflare Dashboard → Pages → Connect Git
  - Select repo: `Tradyxa-Aztryx`
  - Build settings:
    - Framework preset: None
    - Build command: `npm run build`
    - Build output directory: `dist`
    - Root directory: `/client`

- [ ] **Enable auto-deployment on git push**
  - Should be automatic with GitHub integration

- [ ] **Test first deployment manually**
  - Make a small change, commit, push
  - Check: Cloudflare deployment starts
  - Check: Dashboard loads successfully

---

## Phase 5: First Workflow Tests

- [ ] **Test live_spot_prices workflow manually**
  - GitHub → Actions → Live Spot Prices Update
  - Click: "Run workflow" → Select branch: main
  - Wait: ~1 minute
  - Verify: `public/data/live/spot_prices.json` updated
  - Check: Contains latest prices

  ```bash
  # After workflow completes
  python -c "import json; data=json.load(open('public/data/live/spot_prices.json')); print(f'Timestamp: {data[\"timestamp\"]}, VIX: {data[\"vix\"]}, Prices count: {len(data[\"prices\"])}')"
  ```

- [ ] **Test daily_update workflow manually**
  - GitHub → Actions → Daily Dashboard Update
  - Click: "Run workflow" → Select branch: main
  - Wait: ~25 minutes
  - Verify: All 503 JSON files updated
  - Check: Each JSON has verdict, regime, Q50, Q90

  ```bash
  # After workflow completes
  python -c "
  import json, glob
  files = glob.glob('public/data/ticker/*.json')
  print(f'Total files: {len(files)}')
  sample = json.load(open(files[0]))
  print(f'Sample {files[0].split(\"/\")[-1]}: verdict={sample.get(\"verdict\")}, regime={sample.get(\"regime\")}, Q90={sample.get(\"slippageQ90\")}')"
  ```

- [ ] **Test train workflow (Optional - runs weekly anyway)**
  - GitHub → Actions → Weekly Model Training
  - Click: "Run workflow" → Select branch: main
  - Wait: ~50 minutes
  - Verify: New models saved
  - Check: Models newer than last week

  ```bash
  # After workflow completes
  ls -lh models/*.joblib | awk '{print $6, $7, $8, $9}'
  ```

---

## Phase 6: Dashboard Verification

- [ ] **Dashboard loads successfully**
  - Open: `https://your-domain.pages.dev/`
  - Should load: React dashboard with all tiles
  - Should NOT show: Errors, blank pages, 404s

- [ ] **Real data visible on dashboard**
  - Select a stock: RELIANCE
  - Verify: Spot price matches live
  - Verify: Volume Profile has 20 buckets
  - Verify: Candles show 60 days
  - Verify: Bollinger Bands calculated
  - Verify: Verdict shows UP/DOWN with score

- [ ] **Live prices update every 30 min**
  - Check: Spot prices auto-refresh
  - Verify: Timestamp in spot_prices.json updates
  - Dashboard should show latest prices without page refresh

- [ ] **Daily data refreshes at 3:45 PM IST**
  - Wait for scheduled time
  - Check: GitHub Actions shows green checkmark
  - Verify: JSONs updated (git log shows recent commits)
  - Dashboard shows fresh data

- [ ] **Weekly training runs on Sunday**
  - Wait for Sunday midnight UTC
  - Check: GitHub Actions completed
  - Verify: New models with today's date
  - Check: Predictions updated in all JSONs

---

## Phase 7: Monitoring Setup

- [ ] **Enable GitHub email notifications**
  - GitHub → Settings → Notifications
  - Check: "Send email when workflows fail"
  - Add email to notifications

- [ ] **Set up Cloudflare alerts (optional)**
  - Cloudflare Dashboard → Notifications
  - Setup: Page Rules, error rates, etc.

- [ ] **Create monitoring script for dashboard health**
  ```bash
  # scripts/health_check.sh
  #!/bin/bash
  
  # Check live prices exist and are recent
  TIMESTAMP=$(python -c "import json; data=json.load(open('public/data/live/spot_prices.json')); print(data['timestamp'])")
  echo "Live prices updated at: $TIMESTAMP"
  
  # Check JSON files count
  TOTAL=$(ls public/data/ticker/*.json | wc -l)
  echo "Total ticker JSONs: $TOTAL"
  
  # Check models exist
  if [ -f "models/rf_execution_regime.joblib" ]; then
    echo "✅ Regime model exists"
  else
    echo "❌ Regime model missing"
  fi
  ```

  ```bash
  chmod +x scripts/health_check.sh
  ./scripts/health_check.sh
  ```

---

## Phase 8: Documentation & Handoff

- [ ] **Create PRODUCTION_DEPLOYMENT_GUIDE.md** ✅
  - How to deploy
  - What each script does
  - Workflow times and frequencies

- [ ] **Create PRODUCTION_SCRIPTS_QUICK_REF.md** ✅
  - Quick reference for scripts
  - Complete execution order
  - Expected times

- [ ] **Create PRODUCTION_DATA_PIPELINE_VISUAL.md** ✅
  - Visual flowcharts
  - Data volume info
  - Performance metrics

- [ ] **Create troubleshooting guide**
  ```markdown
  # Troubleshooting Guide

  ## Workflow failed
  1. Check GitHub Actions logs
  2. Common issues:
     - Rate limits from Yahoo Finance → increase wait time
     - Out of memory → reduce workers
     - File not found → verify paths

  ## Dashboard showing old data
  1. Check: Latest JSON timestamps
  2. Check: Cloudflare cache cleared
  3. Force refresh: Ctrl+Shift+R

  ## Live prices not updating
  1. Check: live_spot_prices.json modified time
  2. Verify: fetch_spot_prices.py not erroring
  3. Check: Cloudflare deployment

  ## Models not training
  1. Check: All JSON files present
  2. Verify: Python dependencies installed
  3. Check: Disk space on runner
  ```

- [ ] **Document API endpoints** (if applicable)
  - GET `/api/ticker/:ticker/full` → Full ticker data
  - GET `/live/spot_prices.json` → Current prices

---

## Phase 9: Post-Launch (First Week)

- [ ] **Monitor first 5 days of workflows**
  - Check all daily updates succeed
  - Verify no errors in logs
  - Confirm data quality

- [ ] **Check live prices update frequency**
  - Verify every 30 min during market hours
  - Verify NO updates outside market hours

- [ ] **Verify incremental data updates**
  - CSVs growing only ~5-10 rows/day (not 5 years)
  - JSON files updating only deltas, not full refresh

- [ ] **Test model predictions**
  - Compare regime classification to market conditions
  - Verify slippage predictions reasonable
  - Check feature importance makes sense

- [ ] **Measure dashboard performance**
  - Page load time: Should be <2s
  - TTI (Time to Interactive): <3s
  - Dashboard responsiveness: Smooth scrolling

- [ ] **User feedback collection**
  - Survey: Is data fresh enough?
  - Survey: Is investment guidance helpful?
  - Survey: Any missing features?

---

## Phase 10: Ongoing Maintenance

- [ ] **Weekly checks**
  - Training workflow completed
  - Models updated
  - No workflow failures

- [ ] **Monthly checks**
  - Data quality review (any anomalies?)
  - Feature importance trends (changing markets?)
  - Disk space usage (CSVs growing too fast?)

- [ ] **Quarterly reviews**
  - Model performance evaluation
  - Feature engineering updates
  - Dashboard UX improvements

- [ ] **Annual maintenance**
  - Refresh all data (clean slate)
  - Archive old CSVs (>1 year)
  - Retrain models with full history

---

## ✅ Final Sign-Off

Once all checkboxes complete, your production dashboard is **live and automated**:

- ✅ 503 stocks with real data
- ✅ 9 tile visualizations per stock
- ✅ Real-time spot prices (every 30 min)
- ✅ Daily data updates (3:45 PM IST)
- ✅ Weekly ML model retraining
- ✅ Adaptive insights (not static)
- ✅ Investment recommendations
- ✅ Global CDN deployment
- ✅ Zero manual intervention

**Dashboard Status: 🚀 PRODUCTION READY**

---

## 📞 Emergency Contacts

If workflows fail:

1. **Check logs:** GitHub Actions → Workflow → View logs
2. **Common fixes:**
   - Rate limiting → Wait 1 hour
   - Out of disk → Reduce worker count
   - Missing files → Verify git push completed
3. **Manual recovery:**
   ```bash
   # Re-run workflow manually
   GitHub → Actions → Select workflow → Run workflow
   ```
4. **Full reset** (if all else fails):
   ```bash
   # Regenerate all data locally
   python scripts/tradyxa_pipeline.py --mode batch_run --tickers-file scripts/nifty500.txt --max-workers 4 --use-yf
   python scripts/train_regime_classifier.py
   python scripts/train_slippage_quantile.py
   python scripts/apply_models.py
   git add .
   git commit -m "chore: manual data regeneration"
   git push
   ```

---

**All production checks complete. Your dashboard is ready for traders! 🎉**
