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

Idle check. Quick scan:
1. gh pr list --repo Molecule-AI/molecule-core --state open --json number,title,statusCheckRollup | head -20
2. Check if any team members need unblocking.
3. If CI-green PRs have approvals: merge them.
4. If nothing to do: commit_memory "idle HH:MM — team clear, no blockers"
