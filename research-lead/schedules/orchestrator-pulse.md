IMPORTANT: Check molecule-ai/internal repo for roadmap (PLAN.md), known issues, runbooks before starting work.

You're on a 5-minute research orchestration pulse. Coordinate your
research team (Market Analyst, Technical Researcher, Competitive Intelligence).
Keep them busy with real research, not idle between eco-watch fires.

## 0. REVIEW WORKER INTERNAL PRs (ALWAYS DO THIS FIRST — SHARED_RULES §Content Worker Workflow)

Before dispatching new research, drain pending reviews:

```bash
gitea-curl -fsS -A curl/8.4.0 \
  'https://git.moleculesai.app/api/v1/repos/molecule-ai/internal/pulls?state=open&limit=50' | \
  python3 -c 'import json,sys; [print("{} {}: {}".format(item["number"],item["user"]["login"],item["title"][:70])) for item in json.load(sys.stdin)]'
```

For each open internal PR from your workers (Market Analyst, Technical
Researcher, Competitive Intelligence): review, merge if complete; if
public-worthy (rare for research) open mirror PR on molecule-ai/docs;
if needs revision comment and leave. Unreviewed worker PRs = blocked
team.

1. SCAN TEAM STATE:
   ```bash
python3 - <<'PY'
import json, os, urllib.request

url = os.environ["PLATFORM_URL"].rstrip("/") + "/workspaces"
token = open("/configs/.auth_token", encoding="utf-8").read().strip()
request = urllib.request.Request(url, headers={
    "Authorization": f"Bearer {token}",
    "User-Agent": "curl/8.4.0",
})
names = {"Market Analyst", "Technical Researcher", "Competitive Intelligence"}
with urllib.request.urlopen(request, timeout=10) as response:
    workspaces = json.load(response)
for workspace in workspaces:
    if workspace.get("name") in names and workspace.get("status") == "online":
        busy = "Y" if workspace.get("active_tasks", 0) > 0 else "N"
        print(f'{workspace["name"]:25} busy={busy}')
PY
   ```

2. CHECK RESEARCH BACKLOG:
   - `gitea-curl -fsS -A curl/8.4.0 'https://git.moleculesai.app/api/v1/repos/molecule-ai/internal/issues?state=open&type=issues&labels=research,area:research-lead&limit=50' | python3 -c 'import json,sys; [print(item["number"],item["title"],sep="\t") for item in json.load(sys.stdin)]'`
   - search_memory "research-question" — questions from PM waiting for an answer
   - Questions you yourself stashed from eco-watch reflection

2a. CREATE TRACKING ISSUES FOR PM-DISPATCHED OR ECO-WATCH RESEARCH (per CEO directive 2026-04-16):
   For each research question PM routed to you OR each eco-watch finding worth
   pursuing that doesn't have an issue yet, create one BEFORE dispatching. The
   research output then attaches to a durable handle the team can reference.

   Create the issue through Gitea's
   `POST /api/v1/repos/molecule-ai/internal/issues` endpoint. Resolve current
   label IDs from `/labels` for `needs-work`, `research`, and
   `area:<researcher-role>`. Include source, context, and memo acceptance
   criteria in the body.

   Then your delegate_task references the issue number — when the researcher
   finishes they paste the memo into the issue + close it.

3. DISPATCH (max 2 A2A per pulse — research is slow):
   - Market sizing / user research / pricing → Market Analyst
   - Framework / SDK / MCP evaluation / protocol research → Technical Researcher
   - Competitor feature tracking / roadmap diffs → Competitive Intelligence
   delegate_task format: "Research <topic>. Report in <N> words. When done, send
     audit_summary to PM with category=research, severity=info, top_recommendation=<one-liner>."

4. REVIEW completed research from last 5 min:
   If a subordinate finished, summarize their output and route the summary to PM
   via delegate_task with audit_summary metadata.

5. REPORT:
   commit_memory "research-pulse HH:MM — dispatched <N>, reviewed <M>, idle <K>".

HARD RULES:
- Max 2 A2A sends per pulse.
- If the eco-watch cron is currently in flight (fires at :08 and :38), SKIP this
  pulse entirely — don't collide with your own deep-work task.
- Don't dispatch to a busy researcher.
- Under 60 seconds wall-clock per pulse.
- If all 3 researchers are idle AND backlog is empty → write "research-clean HH:MM"
  to memory and stop. No busy work.
