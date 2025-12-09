# Cloudflare Pages Configuration

## Setup Steps

### 1. Connect Your Repository
1. Go to Cloudflare Dashboard → Pages
2. Click "Create a project" → "Connect to Git"
3. Select your GitHub repository `zetaaztra/Gammax`
4. Authorize Cloudflare

### 2. Configure Build Settings

In Cloudflare Pages dashboard:

**Framework**: None (Manual build)

**Build command**: 
```bash
npm run build
```

**Build output directory**: 
```
dist
```

**Environment variables**: (optional)
```
ENVIRONMENT = production
```

### 3. Node Version
- The `.node-version` file specifies Node 22
- Cloudflare will use this automatically

### 4. What Happens on Deploy

```
1. GitHub push to main branch
   ↓
2. Cloudflare Pages detects changes
   ↓
3. Runs: npm ci
   ↓
4. Runs: npm run build  ← Builds TypeScript/React
   ↓
5. Deploys dist/ folder to CDN
   ↓
6. Site is live!
```

## File Structure

```
wrangler.toml              ← Pages config (minimal)
package.json               ← npm build command
.node-version              ← Node 22
dist/                      ← Output (served by Cloudflare)
public/data/               ← Static JSON data (served)
```

## Why No Python?

- ✓ `requirements-github-actions.txt` is NOT in root (Cloudflare won't see it)
- ✓ wrangler.toml has NO Python references
- ✓ Only Node.js build happens on Cloudflare

## Testing Locally

```bash
npm run build  # Create dist/ folder
npm run start  # Run production build
```

Then deploy to Cloudflare:
```bash
git push origin main
```

Cloudflare will auto-deploy!
