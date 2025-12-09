# Build Output Structure Fixed

## The Problem

Build was outputting to:
```
dist/
  ├── public/          ← Frontend files here
  │   ├── assets/
  │   └── index.html
  ├── index.cjs        ← Server file
  └── public/data/     ← Static data
```

Cloudflare Pages looks for `index.html` directly in `dist/`, not in `dist/public/`.

## The Solution

Fixed `vite.config.ts` to output frontend directly to `dist/`:

```typescript
build: {
  outDir: path.resolve(import.meta.dirname, "dist"),
  emptyOutDir: false,  // Don't delete server files
}
```

Fixed `script/build.ts` to not delete the entire dist folder:

```typescript
// Clean only index.cjs, not entire dist folder
try {
  await rm("dist/index.cjs", { force: true });
} catch (e) {
  // File might not exist, that's okay
}
```

## New Build Output Structure

```
dist/
  ├── index.html           ← Frontend entry (Cloudflare serves this)
  ├── assets/
  │   ├── index-*.css
  │   └── index-*.js
  ├── index.cjs            ← Server bundle
  ├── public/data/         ← Static JSON data
  ├── manifest.json
  ├── robots.txt
  └── sitemap.xml
```

## What Changed

1. **vite.config.ts**: Changed `outDir` from `dist/public` to `dist`
2. **script/build.ts**: Don't delete entire `dist/` folder anymore
3. Build now works correctly with Cloudflare Pages

## Testing Locally

```bash
npm run build
# Creates dist/ with index.html at root
```

## Next Steps

1. Cloudflare will auto-detect the new commit
2. Build runs: `npm run build`
3. Deploys `dist/` folder
4. Site will be accessible with content!

Your site should now work! 🚀
