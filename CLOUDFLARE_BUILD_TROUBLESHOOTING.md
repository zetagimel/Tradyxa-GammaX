# Cloudflare Pages Build Troubleshooting

## Important: wrangler.toml Cannot Have Build Command

**Cloudflare Pages DOES NOT support** the `build` key in `wrangler.toml`. You MUST configure the build command in the Cloudflare dashboard instead.

## Configuration Files

### wrangler.toml (For Pages ONLY)
```toml
name = "tradyxa"
compatibility_date = "2024-12-06"
pages_build_output_dir = "dist"
```

That's it! No `[build]` section.

### .npmrc
```
optional = true
```

This allows npm to install optional dependencies like native rollup modules.

## REQUIRED: Cloudflare Dashboard Setup

You MUST configure this in Cloudflare Pages dashboard:

### Steps:
1. Go to **Cloudflare Dashboard** → **Pages**
2. Select your project
3. Click **Settings** → **Build and deployments**
4. Under "Build settings":
   - **Build command**: `npm run build`
   - **Build output directory**: `dist`
5. **Save and deploy**

Without this configuration in the dashboard, the build will fail.

## Why This Matters

- **wrangler.toml** for Pages = minimal config only
- **Cloudflare Dashboard** = where build commands go
- Pages doesn't read build commands from wrangler.toml

## Testing Locally

Before pushing to Cloudflare, test the build:

```bash
# Remove node_modules and package-lock.json
rm -r node_modules package-lock.json

# Reinstall
npm install

# Build
npm run build

# Should create dist/ folder with compiled code
```

If that works locally, it will work on Cloudflare.

## Common Issues

### "Configuration file for Pages projects does not support 'build'"
- Remove the `[build]` section from `wrangler.toml`
- Use the dashboard instead

### Still seeing build errors?
1. Check dashboard settings (Build command & output directory)
2. Verify wrangler.toml has NO build section
3. Try manually triggering a redeploy in dashboard

### Module not found errors?
- Delete `node_modules` and `package-lock.json` locally
- Run `npm install` again
- Verify all files exist in `script/` and `server/` directories

