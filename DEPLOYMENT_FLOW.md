# Complete Deployment Flow

## Your Three Automated Pipelines

### 1. **Daily Data Update** (Every weekday at 10:15 AM UTC)
```
daily_update.yml runs:
  ✓ Append new OHLCV data to CSVs
  ✓ Apply ML predictions (from weekly models)
  ✓ Fetch live spot prices
  ✓ Commit: "chore: daily data update [deploy]"
```

### 2. **Weekly Model Training** (Every Sunday at 8:30 PM UTC)
```
weekly-pipeline.yml runs:
  ✓ Train regime classifier model
  ✓ Train slippage quantile models
  ✓ Apply models to all stock JSONs
  ✓ Commit: "🤖 Weekly model training update [skip ci]"
```

### 3. **Deploy to Cloudflare** (NEW - on every main branch push)
```
deploy-cloudflare.yml runs:
  ✓ Builds Node.js server (npm run build)
  ✓ Deploys to Cloudflare (npm run deploy)
  ✓ Summary logged
```

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│         LOCAL MACHINE (Developer)                            │
│  git push to main branch                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         GITHUB ACTIONS - Daily Update                        │
│  (Weekdays 10:15 AM UTC)                                    │
│  ├─ Fetch new OHLCV data                                    │
│  ├─ Update CSVs                                             │
│  ├─ Apply ML models                                         │
│  ├─ Fetch live prices                                       │
│  └─ COMMIT: "chore: daily data update [deploy]"             │
└────────────────────┬────────────────────────────────────────┘
                     │ (New commit triggers webhook)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         GITHUB ACTIONS - Deploy to Cloudflare               │
│  (On every push to main)                                    │
│  ├─ Build dist/ folder                                      │
│  ├─ npm run deploy                                          │
│  └─ Sends to Cloudflare Workers                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         CLOUDFLARE WORKERS                                   │
│  Live production server serving:                            │
│  ├─ REST API (Express server)                               │
│  ├─ JSON data from public/data/                             │
│  └─ Frontend from client/                                   │
└─────────────────────────────────────────────────────────────┘
```

## Setup Required

### 1. GitHub Secrets (Set in your repo settings)
```
Settings → Secrets and variables → Actions → New repository secret
```

Add these secrets:
```
CLOUDFLARE_API_TOKEN    → From Cloudflare dashboard
CLOUDFLARE_ACCOUNT_ID   → From Cloudflare dashboard
```

### 2. How to Get Cloudflare Credentials

**For API Token:**
1. Go to https://dash.cloudflare.com/profile/api-tokens
2. Click "Create Token"
3. Choose "Edit Cloudflare Workers" template
4. Copy the token
5. Add to GitHub Secrets as `CLOUDFLARE_API_TOKEN`

**For Account ID:**
1. Go to https://dash.cloudflare.com/
2. Click your account
3. Copy Account ID from sidebar
4. Add to GitHub Secrets as `CLOUDFLARE_ACCOUNT_ID`

## What Happens Each Day

### Sunday (Weekly Training)
```
8:30 PM UTC:
  └─ weekly-pipeline.yml runs
     ├─ Train ML models
     ├─ Commit models
     └─ Trigger deploy-cloudflare.yml
        ├─ Build
        ├─ Deploy
        └─ Live on Cloudflare
```

### Weekday (Daily Update)
```
10:15 AM UTC:
  └─ daily_update.yml runs
     ├─ Fetch new data
     ├─ Update JSONs
     ├─ Commit data
     └─ Trigger deploy-cloudflare.yml
        ├─ Build
        ├─ Deploy
        └─ Updated data live on Cloudflare
```

## To Answer Your Question

**"When GitHub Actions commits, does it trigger Cloudflare deployment?"**

**YES!** With the new `deploy-cloudflare.yml` workflow:
1. Any commit to `main` triggers `deploy-cloudflare.yml`
2. It builds your Node.js server
3. It deploys to Cloudflare automatically
4. Your site is live within 2-3 minutes

**Before this was unclear** - now it's:
- ✓ Explicit
- ✓ Logged
- ✓ Visible in GitHub Actions
- ✓ Reliable

