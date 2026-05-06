Landing page SEO audit. You co-own Molecule-AI/landingpage with Content Marketer.

## Step 1: Check repo
```bash
gh pr list --repo Molecule-AI/landingpage --state open --json number,title
gh issue list --repo Molecule-AI/landingpage --state open --json number,title
```

## Step 2: SEO checks
- Review any open PRs that touch SEO-related files (meta tags, structured data, sitemap)
- Check if og:image, og:title, og:description are set correctly for each page
- Verify sitemap is generating correctly
- Check for i18n hreflang tags (en + zh)

## Step 3: Act
Clone and fix if needed:
```bash
git clone https://x-access-token:${GITHUB_TOKEN}@github.com/Molecule-AI/landingpage.git /workspace/repos/landingpage 2>/dev/null || (cd /workspace/repos/landingpage && git pull)
```

## Step 4: Report
commit_memory "landingpage-seo HH:MM — PRs: N, issues: N, SEO status: <ok or findings>"
