Idle check. Quick scan:
1. Query the first 20 open `molecule-ai/molecule-core` PRs through Gitea's `/pulls` API and verify each head SHA's current commit-status rollup.
2. Check if any team members need unblocking.
3. If CI-green PRs have approvals: merge them.
4. If nothing to do: commit_memory "idle HH:MM — team clear, no blockers"
