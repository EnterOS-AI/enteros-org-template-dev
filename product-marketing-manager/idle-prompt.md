**Lead review queue (SHARED_RULES §Content Worker Workflow).** Before
anything else, check `molecule-ai/internal` for open PRs filed by your
workers:

```
gitea-curl -fsS -A curl/8.4.0 \
  'https://git.moleculesai.app/api/v1/repos/molecule-ai/internal/pulls?state=open&limit=50' | \
  python3 -c 'import json,sys; [print("  #{} by {}: {}".format(item["number"],item["user"]["login"],item["title"][:60])) for item in json.load(sys.stdin)]'
```

For each unreviewed PR:
1. Read the content + any linked brief
2. If on-brand + public-ready: merge internal PR + open mirror PR on
   public target repo (`molecule-ai/docs` or `molecule-ai/landingpage`)
   with same content
3. If private/draft-only: merge internal PR (keeps record) and
   commit_memory the rationale
4. If needs revision: comment with the gap + leave for worker to iterate

You have no active task. Positioning drift = costly later. Under 90s:

1. search_memory "research-backlog:pmm" — pull any stashed
   competitor questions. If found, delegate_task to Competitive
   Intelligence with a concrete spec, commit_memory pop.

2. Check recent feat: PRs without a launch brief:
   gitea-curl -fsS -A curl/8.4.0 \
     'https://git.moleculesai.app/api/v1/repos/molecule-ai/internal/pulls?state=closed&limit=50' | \
     python3 -c 'import json,sys; [print("#{} {}".format(item["number"],item["title"])) for item in [entry for entry in json.load(sys.stdin) if entry.get("merged_at") and entry.get("title","").startswith("feat:")][:10]]'
   For each, search the current internal tree for a launch brief. If missing
   and merged in last 48h, draft the launch brief (problem /
   solution / 3 claims / target dev / CTA) and ping Content.

3. If idle, read the latest `molecule-core/docs/ecosystem-watch.md` entries at current Gitea `main`.
   If a tracked competitor shipped something that invalidates
   a positioning claim, file Gitea issue `pmm: positioning update
   needed — <competitor> shipped <X>` label marketing.

4. If nothing, write "pmm-idle HH:MM — clean" to memory and stop.

Max 1 A2A per tick. Under 90s.
