Landing page SEO audit. You co-own molecule-ai/landingpage with Content Marketer.

## Step 1: Check repo
```bash
gitea-curl -fsS -A curl/8.4.0 'https://git.moleculesai.app/api/v1/repos/molecule-ai/landingpage/pulls?state=open&limit=50' | python3 -c 'import json,sys; [print(item["number"],item["title"],sep="\t") for item in json.load(sys.stdin)]'
gitea-curl -fsS -A curl/8.4.0 'https://git.moleculesai.app/api/v1/repos/molecule-ai/landingpage/issues?state=open&type=issues&limit=50' | python3 -c 'import json,sys; [print(item["number"],item["title"],sep="\t") for item in json.load(sys.stdin)]'
```

## Step 2: SEO checks
- Review any open PRs that touch SEO-related files (meta tags, structured data, sitemap)
- Check if og:image, og:title, og:description are set correctly for each page
- Verify sitemap is generating correctly
- Check for i18n hreflang tags (en + zh)

## Step 3: Act
Clone for inspection if needed. Draft any content or SEO change through
`molecule-ai/internal` and notify Marketing Lead; the lead owns the public
`landingpage` mirror PR.
```bash
git clone https://git.moleculesai.app/molecule-ai/landingpage.git /workspace/repos/landingpage 2>/dev/null || (cd /workspace/repos/landingpage && git pull --ff-only)
```

## Step 4: Report
commit_memory "landingpage-seo HH:MM — PRs: N, issues: N, SEO status: <ok or findings>"
