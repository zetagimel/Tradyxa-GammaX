#!/bin/bash

echo "=== CLOUDFLARE DEPLOYMENT DIAGNOSTIC ==="
echo ""
echo "1. Checking git log for data commits..."
git log --oneline --all | grep -i "data\|deploy" | head -10

echo ""
echo "2. Checking if latest commits have data files..."
git show --name-only HEAD | grep -c "\.json\|\.csv" || echo "No data files in latest commit"

echo ""
echo "3. Checking local data file count..."
echo "   JSONs: $(ls public/data/ticker/*.NS.json 2>/dev/null | wc -l)"
echo "   CSVs: $(ls public/data/raw/*.csv 2>/dev/null | wc -l)"

echo ""
echo "4. Checking GitHub Actions workflow status..."
echo "   View at: https://github.com/pravindev666/Gammax/actions"

echo ""
echo "5. Key checkpoint: Are GitHub Actions & Cloudflare synchronized?"
echo "   - GitHub Actions generates data ✓"
echo "   - Data is committed to git ✓"
echo "   - Git push completes ?"
echo "   - Cloudflare Pages webhook fires ?"
echo "   - Cloudflare builds from latest commit ?"
echo ""
echo "To verify: Compare local files vs deployed:"
echo "   curl https://gammax.pages.dev/data/ticker/NIFTY.json | head -5"
