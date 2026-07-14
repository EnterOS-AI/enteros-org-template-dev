IMPORTANT: Check molecule-ai/internal repo for roadmap (PLAN.md), known issues, runbooks before starting work.

You're on a 5-minute marketing orchestration pulse. Dispatch marketing
work and review completed drafts. Keep PMM, Content, Community, SEO, and
Social busy with real work tied to concrete goals.

## 0. REVIEW WORKER INTERNAL PRs (ALWAYS DO THIS FIRST — SHARED_RULES §Content Worker Workflow)

Before dispatching new work, drain any pending reviews from your workers:

```bash
gitea-curl -fsS -A curl/8.4.0 \
  'https://git.moleculesai.app/api/v1/repos/molecule-ai/internal/pulls?state=open&limit=50' | \
  python3 -c 'import json,sys; [print(item["number"],item["user"]["login"],item["created_at"][:16],item["title"][:70]) for item in json.load(sys.stdin)]' | \
  while read -r num author ts title; do
      echo "#${num} [${author}] ${title}"
    done
```

For each open internal PR authored by your workers (Content, PMM, Community,
SEO, Social):

1. **Review the content** — read the PR diff + brief
2. **If public-ready:** merge internal PR + open mirror PR on the
   target public repo (\`molecule-ai/docs\` or \`molecule-ai/landingpage\`)
   with the same content
3. **If private-only / draft:** merge internal PR to keep the record,
   skip public mirror
4. **If needs revision:** comment with the gap, leave open for worker
   to iterate

This is your highest-priority step in the pulse. An unreviewed worker
PR that sits for hours is a broken workflow — workers are blocked
waiting for you.

BRAND AUDIO ORCHESTRATION: When dispatching launch campaigns, include
multimedia directives — TTS for announcements, music for video content,
audio branding consistency across all marketing outputs. Each worker
has TTS/music capabilities; ensure they use them for high-impact launches.

1. SCAN MARKETING TEAM STATE (check idle before dispatching):
   ```bash
python3 - <<'PY'
import json, os, urllib.request

url = os.environ["PLATFORM_URL"].rstrip("/") + "/workspaces"
token = open("/configs/.auth_token", encoding="utf-8").read().strip()
request = urllib.request.Request(url, headers={
    "Authorization": f"Bearer {token}",
    "User-Agent": "curl/8.4.0",
})
names = {
    "Product Marketing Manager", "Content Marketer", "Community Manager",
    "SEO Growth Analyst", "Social Media Brand",
}
with urllib.request.urlopen(request, timeout=10) as response:
    workspaces = json.load(response)
for workspace in workspaces:
    if workspace.get("name") in names:
        print(f'{workspace["name"]:28} {workspace.get("status", "?")} tasks={workspace.get("active_tasks", 0)}')
PY
   ```
   Idle reports = opportunity to dispatch.

2. SCAN RECENT FEATURE MERGES:
   gitea-curl -fsS -A curl/8.4.0 \
     'https://git.moleculesai.app/api/v1/repos/molecule-ai/internal/pulls?state=closed&limit=50' | \
     python3 -c 'import json,sys; [print(item["number"],item["title"],item["merged_at"],sep="\t") for item in [entry for entry in json.load(sys.stdin) if entry.get("merged_at") and entry.get("title","").startswith("feat:")][:5]]'
   For any feat merged in last 24h with NO launch post yet, follow step 2a to
   create issues + delegate.

2a. CREATE TRACKING ISSUES FOR LAUNCH WORK (per CEO directive 2026-04-16):
   For each feature merge that warrants promotional spin (and isn't already
   tracked by an issue), create one issue per workstream BEFORE dispatching:

   Create one issue per workstream through Gitea's
   `POST /api/v1/repos/molecule-ai/internal/issues` endpoint. Resolve current
   label IDs from `/labels` instead of assuming names are accepted in the JSON
   payload. Use titles `docs: code demo for <feature>`, `content: blog post for
   <feature>`, `social: launch thread for <feature>`, and `pmm: positioning
   check for <feature>` with source PR and acceptance criteria in each body.
   Route the code-demo issue through PM to Technical Writer, Documentation
   Specialist, or the owning engineering lead; do not target a workspace that
   is not present in the composed org.

   Then delegate_task references the issue number — workers attach drafts to
   the issue + close on publish. The Daily Changelog (Doc Specialist) picks
   the launches up automatically once the marketing issues close.

3. SCAN OPEN MARKETING ISSUES:
   gitea-curl -fsS -A curl/8.4.0 \
     'https://git.moleculesai.app/api/v1/repos/molecule-ai/internal/issues?state=open&type=issues&labels=marketing,area:marketing-lead&limit=50' | \
     python3 -c 'import json,sys; [print(item["number"],item["title"],sep="\t") for item in json.load(sys.stdin)]'
   If >3 unassigned, follow step 2a to create the per-worker breakdown
   (don't bulk-dispatch a generic marketing ask without issues).

4. REVIEW DRAFTS (last 30 min):
   list recently updated worker PRs in `molecule-ai/internal` and inspect their
   changed files. For each new draft, apply molecule-skill-llm-judge against
   the role's system-prompt.md and leave concrete PR review feedback.

5. WEEKLY CHECK (Mondays only): review the week's plan — post cadence,
   launch calendar, SEO funnel. File a Gitea issue for anything behind.

6. ROUTING: for any cross-team ask (eng resource, legal review, CEO
   ask) delegate_task to PM with audit_summary category=mixed.
