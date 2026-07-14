Landing page health check. You co-own molecule-ai/landingpage with SEO Analyst.

## Step 1: Check repo activity
```bash
gitea-curl -fsS -A curl/8.4.0 https://git.moleculesai.app/api/v1/repos/molecule-ai/landingpage | python3 -c 'import json,sys; data=json.load(sys.stdin); print(json.dumps({key:data.get(key) for key in ("updated_at","default_branch")},indent=2))'
gitea-curl -fsS -A curl/8.4.0 'https://git.moleculesai.app/api/v1/repos/molecule-ai/landingpage/pulls?state=open&limit=50' | python3 -c 'import json,sys; [print(item["number"],item["title"],item["user"]["login"],sep="\t") for item in json.load(sys.stdin)]'
gitea-curl -fsS -A curl/8.4.0 'https://git.moleculesai.app/api/v1/repos/molecule-ai/landingpage/issues?state=open&type=issues&limit=50' | python3 -c 'import json,sys; [print(item["number"],item["title"],sep="\t") for item in json.load(sys.stdin)]'
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
Clone the repo for inspection when needed. If you find a content change, draft
it through `molecule-ai/internal` and notify Marketing Lead; the lead owns the
public `landingpage` mirror PR.
```bash
git clone https://git.moleculesai.app/molecule-ai/landingpage.git /workspace/repos/landingpage 2>/dev/null || (cd /workspace/repos/landingpage && git pull --ff-only)
```

## Step 5: Report
commit_memory "landingpage-check HH:MM — PRs: N open, issues: N, acted on: <list or none>"
