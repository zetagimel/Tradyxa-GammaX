# JSON Data Files Deployment Fix

## The Problem

Deployment was successful but no data showed up because:
1. JSON files weren't being copied to the build output (`dist/`)
2. Server was looking for files in `public/data/` which didn't exist in the deployed build

## The Solution

### 1. Build Script Update (`script/build.ts`)

Added data file copying after Vite builds:

```typescript
console.log("copying data files...");
// Copy public/data folder to dist/ (for serving API data)
try {
  await cp("public/data", "dist/data", { recursive: true, force: true });
  console.log("✓ Data files copied to dist/data");
} catch (e) {
  console.warn("⚠ Could not copy data files:", e);
}
```

This copies ~2026 files (CSVs, JSONs, metadata) to `dist/data/`.

### 2. Server Routes Update (`server/routes.ts`)

Changed hardcoded paths to dynamic paths that work in both dev and production:

**Before:**
```typescript
const liveData = await readJsonFile('public/data/live/spot_prices.json');
```

**After:**
```typescript
// Determine data directory (works in both dev and production)
const getDataDir = () => {
  const prodPath = path.join(process.cwd(), "data");
  if (fs.existsSync(prodPath)) return prodPath;
  return path.join(process.cwd(), "public", "data");
};

const DATA_DIR = getDataDir();
const liveData = await readJsonFile(path.join(DATA_DIR, 'live', 'spot_prices.json'));
```

## Build Output Structure Now

```
dist/
  ├── index.html              ← Frontend entry
  ├── assets/                 ← React app JS/CSS
  ├── index.cjs               ← Node.js server
  ├── data/                   ← JSON & CSV files (2026 files)
  │   ├── ticker/             ← Stock data JSONs
  │   ├── raw/                ← Raw CSV files
  │   └── live/               ← Live prices
  ├── public/                 ← Static images/icons
  └── [other static assets]
```

## What Happens on Deployment

1. Cloudflare pulls latest repo
2. Runs: `npm run build`
3. Build:
   - Compiles React to `dist/`
   - Copies 2026 data files to `dist/data/`
   - Bundles server to `dist/index.cjs`
4. Deploys entire `dist/` folder
5. Server looks in `dist/data/` for JSONs (works!)
6. API returns ticker data ✓

## Verification

Local build now shows:
```
✓ Data files copied to dist/data
```

Your data should now be visible after the next deployment! 🎉
