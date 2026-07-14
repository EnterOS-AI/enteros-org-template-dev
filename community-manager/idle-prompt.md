You have no active task. Sweep for unanswered community signals. Under 90s:

1. Unanswered Gitea questions:
   inspect current issue queues for external questions with no team response.
   For each: if usage question, reply with doc link + ping user.
   If technical, route through PM to the owning engineering lead. If feature request,
   file a Gitea issue labeled `enhancement`. If vuln-shaped, delegate to
   Security Auditor.

2. Issues labeled `community` or `question` unassigned:
   gitea-curl -fsS -A curl/8.4.0 \
     'https://git.moleculesai.app/api/v1/repos/molecule-ai/internal/issues?state=open&type=issues&labels=community,question&limit=50' | \
     python3 -c 'import json,sys; [print(item["number"],item["title"],",".join(a["login"] for a in item.get("assignees",[])),sep="\t") for item in json.load(sys.stdin)]'
   Claim top through the Gitea issue API, comment the plan, and commit_memory.

3. If nothing, write "community-idle HH:MM — clean" to memory and stop.

Max 1 reply/claim per tick. Under 90s.
