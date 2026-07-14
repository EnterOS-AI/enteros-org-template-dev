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

Idle check. Quick scan:
1. Query the first 20 open `molecule-ai/molecule-core` PRs through Gitea's `/pulls` API and verify each head SHA's current commit-status rollup.
2. Check if any team members need unblocking.
3. If CI-green PRs have approvals: merge them.
4. If nothing to do: commit_memory "idle HH:MM — team clear, no blockers"
