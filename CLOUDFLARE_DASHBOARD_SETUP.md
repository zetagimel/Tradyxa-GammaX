# Cloudflare Pages Dashboard Setup

## Quick Reference

### Build Command
```
npm run build
```

### Output Directory  
```
dist
```

### Root Directory
```
/
```

### Screenshot Guide

1. **Go to**: Cloudflare Dashboard → Pages
2. **Click**: Your project (or create one)
3. **Settings** tab → **Build and deployments**
4. **Build command**: Enter `npm run build`
5. **Build output directory**: Enter `dist`
6. **Save and deploy**

### Environment Variables (Optional)
```
Name: ENVIRONMENT
Value: production
```

Then redeploy the site.

### After Configuration

Every push to `main` branch will:
- Trigger Cloudflare deployment
- Run `npm run build`
- Deploy `dist/` folder
- Site goes live

## Troubleshooting

### Build Still Fails?
- Check build logs in Cloudflare dashboard
- Verify Node version: `.node-version` file exists
- Run locally: `npm run build` to test

### Python Still Installing?
- Make sure `requirements.txt` doesn't exist
- Only `requirements-github-actions.txt` should exist
- Check wrangler.toml has no `[build]` section

### Site Not Updating?
- Clear browser cache (Ctrl+Shift+Del)
- Wait 1-2 minutes for CDN propagation
- Check deployment status in Cloudflare dashboard
