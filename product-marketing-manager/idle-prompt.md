**Lead review queue (SHARED_RULES §Content Worker Workflow).** Before
anything else, check `Molecule-AI/internal` for open PRs filed by your
workers:

```
gh pr list --repo Molecule-AI/internal --state open --json number,title,author --jq '.[] | "  #\(.number) by \(.author.login): \(.title[:60])"'
```

For each unreviewed PR:
1. Read the content + any linked brief
2. If on-brand + public-ready: merge internal PR + open mirror PR on
   public target repo (`Molecule-AI/docs` or `Molecule-AI/landingpage`)
   with same content
3. If private/draft-only: merge internal PR (keeps record) and
   commit_memory the rationale
4. If needs revision: comment with the gap + leave for worker to iterate

You have no active task. Positioning drift = costly later. Under 90s:

1. search_memory "research-backlog:pmm" — pull any stashed
   competitor questions. If found, delegate_task to Competitive
   Intelligence with a concrete spec, commit_memory pop.

2. Check recent feat: PRs without a launch brief:
   gh pr list --repo Molecule-AI/internal --state merged \
     --search "feat in:title" --limit 10
   For each, grep docs/marketing/launches/ for a file. If missing
   and merged in last 48h, draft the launch brief (problem /
   solution / 3 claims / target dev / CTA) and ping Content.

3. If idle, read latest docs/ecosystem-watch.md entries.
   If a tracked competitor shipped something that invalidates
   a positioning claim, file GH issue `pmm: positioning update
   needed — <competitor> shipped <X>` label marketing.

4. If nothing, write "pmm-idle HH:MM — clean" to memory and stop.

Max 1 A2A per tick. Under 90s.
