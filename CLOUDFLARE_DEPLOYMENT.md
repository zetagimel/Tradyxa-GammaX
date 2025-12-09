# Three-Environment Deployment Architecture

## File Structure
```
requirements.txt      → GitHub Actions (for ML training)
requirements-dev.txt  → Local development (same as requirements.txt)
wrangler.toml         → Cloudflare (NO Python)
```

## GitHub Actions Workflow
```bash
# .github/workflows/weekly-pipeline.yml
- Setup Python 3.12
- pip install -r requirements.txt  ← USES full requirements.txt
- python scripts/train_regime_classifier.py
- python scripts/train_slippage_quantile.py
- git commit & push (models saved as JSON)
```

**Result:** Models trained, JSON files in `public/data/`, committed to repo ✓

## Local Development
```bash
# Install same dependencies as GitHub Actions
pip install -r requirements.txt

# Run ML training locally
python scripts/train_regime_classifier.py
python scripts/train_slippage_quantile.py

# Or use requirements-dev.txt (identical)
pip install -r requirements-dev.txt
```

## Cloudflare Deployment
```bash
# Build Node.js server (NO Python)
npm run build

# Deploy to Cloudflare (pure TypeScript/JavaScript)
npm run deploy
# or
wrangler deploy
```

**Key:** wrangler.toml has NO Python references. It only runs:
- Node.js build process
- TypeScript compilation
- Express server startup

**Result:** Deploys in ~30 seconds ✓

## Workflow Diagram
```
LOCAL MACHINE
    ↓
Train ML Models (requires Python)
    ↓
Save Models as JSON → Git Push
    ↓
GITHUB ACTIONS
    ↓
Pull Latest Data
Train Models (requirements.txt)
    ↓
Commit Generated JSONs
    ↓
CLOUDFLARE
    ↓
Build Server (NO Python needed)
    ↓
Deploy Static + API Endpoints
Serve JSON files to frontend
```

## Why This Works
- ✓ GitHub Actions: Has Python, full build time ~5-10 min
- ✓ Cloudflare: No Python, fast builds ~30 sec
- ✓ Local: Full environment for testing
- ✓ requirements.txt: Used by both GitHub Actions AND local

