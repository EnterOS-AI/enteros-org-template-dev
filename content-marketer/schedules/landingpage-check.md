Landing page health check. You co-own Molecule-AI/landingpage with SEO Analyst.

## Step 1: Check repo activity
```bash
gh repo view Molecule-AI/landingpage --json updatedAt,defaultBranchRef
gh pr list --repo Molecule-AI/landingpage --state open --json number,title,author
gh issue list --repo Molecule-AI/landingpage --state open --json number,title
```

## Step 2: Check for issues
- Open PRs that need review → review them
- Open issues → self-assign and fix
- If no issues: check the live site for broken links, outdated content, missing pages

## Step 3: Content freshness
- Is the landing page copy up to date with the latest product features?
- Are blog references current?
- Is the Chinese translation (zh/) in sync with English?

## Step 4: Act
If you find something to fix: clone the repo, create a branch, fix it, push, open PR.
```bash
git clone https://x-access-token:${GITHUB_TOKEN}@github.com/Molecule-AI/landingpage.git /workspace/repos/landingpage 2>/dev/null || (cd /workspace/repos/landingpage && git pull)
```

## Step 5: Report
commit_memory "landingpage-check HH:MM — PRs: N open, issues: N, acted on: <list or none>"
