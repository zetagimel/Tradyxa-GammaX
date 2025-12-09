# Cost Estimation: GitHub Actions + Cloudflare Pages

## Current Setup

Your system:
- **GitHub Actions**: Runs 2 workflows daily
  - `daily_update.yml`: CSV fetch + JSON generation + ML models + live prices
  - `live_spot_prices.yml`: Live prices update every 2 hours (4 times/day)
  - `weekly-pipeline.yml`: Model training (1x/week)
  
- **Cloudflare Pages**: Hosts static website
  - 502 stocks × 3 files each = ~1,500 JSON files
  - ~2,000 total data files (CSVs + JSONs)
  - ~100-200 MB total

---

## COST BREAKDOWN

### 1. GitHub Actions (Private Repo)

**GitHub Actions Pricing:**
- **Free tier**: 2,000 minutes/month per account
- **After free tier**: $0.25 per 1,000 minutes on Linux

**Your Monthly Usage:**

```
Daily Update Workflow:
- Fetch CSVs: ~15 minutes
- Generate JSONs (502 stocks): ~30 minutes
- Apply ML models: ~5 minutes
- Total per run: ~50 minutes
- Runs daily (5 days/week) = 250 minutes/month

Live Spot Prices Workflow:
- Fetch 502 prices: ~3 minutes
- Runs 4 times/day × 5 days/week = ~60 minutes/month

Weekly Pipeline (Model Training):
- Train regime classifier: ~20 minutes
- Train slippage quantile regressors: ~20 minutes
- Total per week: ~40 minutes × 4 weeks = 160 minutes/month

TOTAL: 250 + 60 + 160 = 470 minutes/month
```

**Cost Estimate:**
- ✅ Well within FREE TIER (2,000 minutes/month)
- 📊 Using only ~23% of free allocation
- 💰 **Cost: $0/month** (FREE!)

---

### 2. Cloudflare Pages

**Cloudflare Pages Pricing:**
- **FREE tier**: 
  - Unlimited deployments
  - Unlimited bandwidth
  - Unlimited sites
  - Support for custom domains
  - SSL/TLS included
  - Global CDN

- **Paid tiers**: Not needed for your use case

**Your Monthly Usage:**

```
Deployments:
- GitHub Actions commits: ~5-10 times/day (auto-triggers)
- Total: ~150-300 deployments/month
- Cloudflare free tier: UNLIMITED ✅

Bandwidth:
- Assume 1,000 daily visitors
- Each visit: ~500 KB (app + data)
- Monthly: 1,000 × 30 × 500 KB = ~15 GB
- Cloudflare free tier: UNLIMITED ✅

Data Storage:
- JSONs + CSVs: ~200 MB
- Cloudflare free tier: No storage limit ✅
```

**Cost Estimate:**
- 💰 **Cost: $0/month** (FREE!)

---

## 🎯 TOTAL MONTHLY COST

| Service | Free Tier | Your Usage | Cost |
|---------|-----------|-----------|------|
| **GitHub Actions** | 2,000 min | 470 min | **$0** |
| **Cloudflare Pages** | Unlimited | 15 GB/month | **$0** |
| **Domain** (optional) | - | - | ~$12/year (~$1/mo) |
| | | | |
| **TOTAL** | | | **$0-1/month** |

---

## When Would You Pay?

### GitHub Actions (Private Repo):
- If you exceed **2,000 minutes/month**
  - You'd need: `2,000 ÷ 50 = 40 daily runs` (impossible)
  - Or very heavy ML training
  - Your current setup is **200% safe**

### Cloudflare Pages:
- The free tier is **genuinely unlimited**
- No hidden costs
- Even with 100,000+ visitors: Still FREE
- You only pay if you upgrade to Cloudflare Pro ($20/mo) for extra features

---

## Cost Comparison: Other Options

### Option A: AWS (What you WOULD pay)
- EC2 instance (t3.small): ~$25-40/month
- S3 storage: ~$5-10/month
- Lambda for scheduled jobs: ~$5-10/month
- **Total: $35-60/month**

### Option B: Heroku (Deprecated, but was)
- Basic dyno: $7-50/month
- Database: $20-200+/month
- **Total: $27-250+/month**

### Option C: Your Setup (GitHub + Cloudflare)
- GitHub Actions: **$0** ✅
- Cloudflare Pages: **$0** ✅
- Custom Domain: $12/year ✅
- **Total: $0-1/month** ✅

---

## Why This Is "Zero Cost"?

1. **GitHub Actions Free Tier**
   - 2,000 minutes = 40 hours/month
   - Most projects use <100 minutes
   - You're using ~470 (23%)
   - Completely FREE

2. **Cloudflare Pages Free Tier**
   - Unlimited deployments
   - Unlimited bandwidth
   - No data storage charges
   - SSL/TLS included
   - Global CDN at no cost
   - "Generous free tier" is their actual policy

3. **No Database Costs**
   - You store everything in GitHub (free)
   - Cloudflare serves static files (free)
   - No API calls needed (pure static)

---

## Budget-Friendly Recommendations

### To Stay at $0/month:
✅ Keep current setup exactly as is
✅ GitHub Actions will never charge you
✅ Cloudflare Pages will never charge you

### If You Need More:
💰 Upgrade path (optional):
- GitHub Pro ($21/mo): More Actions minutes + features
  - But you don't need it (only using 470/2,000)
- Cloudflare Pro ($20/mo): Extra security features
  - But free tier has everything you need

### Your Annual Cost:
- Domain registration: ~$12/year (optional)
- **GitHub + Cloudflare: $0/year**
- **TOTAL: $12/year** (optional domain)

---

## What "Zero Cost Deployment" Means

> "Zero cost deployment" = You can deploy an infinite number of times without paying anything

Your system:
- ✅ Deploys 5-10 times daily (GitHub Actions commits)
- ✅ Each deployment is completely free
- ✅ Even 100 deployments/day would be free
- ✅ Bandwidth is unlimited and free
- ✅ Storage is free
- ✅ Global CDN is free

**This is legitimately zero cost** because:
1. Cloudflare's business model is to use the free tier to gain users, then upsell them later
2. GitHub Actions gives away computing time to open-source and student projects
3. Your use case is so small it barely registers on their infrastructure

---

## Bottom Line

| Question | Answer |
|----------|--------|
| Will GitHub Actions charge you? | **NO** (470 min < 2,000 min free) |
| Will Cloudflare Pages charge you? | **NO** (unlimited free tier) |
| Can you afford this deployment? | **YES** (it's completely free) |
| Should you worry about costs? | **NO** - keep deploying with confidence |
| What if traffic increases 10x? | Still free on Cloudflare |
| What if you run more ML jobs? | Still free (2,000 min/mo available) |

✅ **You can confidently keep this setup without worrying about costs.**
