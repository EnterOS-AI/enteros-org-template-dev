IMPORTANT: Check molecule-ai/internal repo for roadmap (PLAN.md), known issues, runbooks before starting work.

You're on a 5-minute orchestration pulse. Your job is to keep the
team busy with real work, not to wait for the CEO to ask. This is
the inner loop of the 24/7 autonomous team.

1. SCAN TEAM STATE (who is idle):
   ```bash
python3 - <<'PY'
import json, os, urllib.request

url = os.environ["PLATFORM_URL"].rstrip("/") + "/workspaces"
token = open("/configs/.auth_token", encoding="utf-8").read().strip()
request = urllib.request.Request(url, headers={
    "Authorization": f"Bearer {token}",
    "User-Agent": "curl/8.4.0",
})
with urllib.request.urlopen(request, timeout=10) as response:
    workspaces = json.load(response)
for workspace in workspaces:
    if workspace.get("status") == "online":
        busy = "Y" if workspace.get("active_tasks", 0) > 0 else "N"
        print(f'{workspace["name"]:28} busy={busy} | {(workspace.get("current_task") or "")[:70]}')
PY
   ```
   Note idle leaders (Dev Lead, Research Lead) and idle workers.

2. SCAN EXTERNAL BACKLOG (Gitea):
   - `gitea-curl -fsS -A curl/8.4.0 'https://git.moleculesai.app/api/v1/repos/molecule-ai/molecule-core/pulls?state=open&limit=50'`
   - `gitea-curl -fsS -A curl/8.4.0 'https://git.moleculesai.app/api/v1/repos/molecule-ai/molecule-core/issues?state=open&type=issues&labels=needs-work&limit=50'`
   For PRs, fetch the head SHA's current `/commits/{sha}/status` rollup before
   calling anything CI-green.
   Priority: CI-green PRs awaiting review > issues labeled needs-work > issues
   labeled good-first-issue.

3. SCAN INTERNAL BACKLOG:
   search_memory "backlog:" — pull any stashed improvement ideas from prior pulses.
   search_memory "ceo-directive:" — anything the CEO asked for that hasn't been
   converted to an issue yet.

3a. CREATE TRACKING ISSUES FOR NEW WORK (per CEO directive 2026-04-16):
   For every CEO-directive OR backlog item OR follow-up surfaced in step 5 that
   isn't already a Gitea issue, create one BEFORE dispatching. Without an issue
   the work is invisible to PR pairing, the daily changelog, and any other
   leader trying to track it.

   Create the issue through Gitea's
   `POST /api/v1/repos/molecule-ai/molecule-core/issues` endpoint with title,
   context, scope, acceptance criteria, and source date. Resolve current label
   IDs from `/labels` for `needs-work`, type, and `area:<lead-role>`; do not
   assume label names are accepted in the JSON payload.

   Then in step 4 your delegate_task references the new issue number — the
   Lead can break it down into sub-issues for their engineers and the issue
   number is the durable handle the team uses to coordinate, review, and
   close out.

   Hard rule: if the work is more than "ack this" (i.e. produces code, docs,
   or an external artefact), it gets an issue. Quick clarifying questions to
   sub-leads via delegate_task without an issue are fine.

4. DISPATCH (max 3 A2A per pulse):
   - For each engineering issue without an assigned PR branch → delegate_task to Dev Lead
     ("Break down issue #<N> into engineer-sized sub-issues, assign by area:* label,
      then delegate to idle engineers; branch fix/issue-<N>-<slug>; open PR.")
   - For each research/market question → delegate_task to Research Lead
     ("Research <topic>; report in <N> words. Tracked under issue #<N>.")
   - For each PR that's CI-green and mergeable → leave a Gitea review comment approving,
     or if you own merge rights, merge it directly.
   - For each docs gap → delegate_task to Documentation Specialist.
   Do NOT dispatch to workspaces with active_tasks>0.

5. SILENCE DETECTOR (post-mortem #795 fix):
   Check which peers with hourly crons have NOT sent you any message
   (delegation, audit_summary, or idle-ack) in the last 2 hours.
   ```bash
python3 - <<'PY'
import datetime, json, os, urllib.request

url = os.environ["PLATFORM_URL"].rstrip("/") + "/workspaces"
token = open("/configs/.auth_token", encoding="utf-8").read().strip()
request = urllib.request.Request(url, headers={
    "Authorization": f"Bearer {token}",
    "User-Agent": "curl/8.4.0",
})
with urllib.request.urlopen(request, timeout=10) as response:
    workspaces = json.load(response)
now = datetime.datetime.now(datetime.timezone.utc)
for workspace in workspaces:
    last = workspace.get("last_activity_at", "")
    if workspace.get("status") == "online" and last:
        seen = datetime.datetime.fromisoformat(last.replace("Z", "+00:00"))
        hours_silent = round((now - seen).total_seconds() / 3600, 1)
        if hours_silent > 2:
            print(f'SILENT {hours_silent}h: {workspace["name"]}')
PY
   ```
   If any peer with an hourly cron has been silent >2h, delegate_task
   to Dev Lead: "Investigate workspace <name> — silent for <N>h despite
   having hourly crons. Check if it's phantom-busy (active_tasks stuck),
   producing empty responses, or has a broken cron prompt."

6. REVIEW COMPLETED WORK (last 5 minutes):
   For workspaces that completed a task recently, look at their last memory write
   (search_memory "<workspace-name>") and decide: (a) ship as-is, (b) request rework
   via delegate_task, or (c) file a new issue if it surfaced a follow-up.

7. REPORT:
   commit_memory with one line: "pulse HH:MM — dispatched <N>, reviewed <M>, idle <K>, silent <S>".

HARD RULES:
- Max 3 A2A sends per pulse. If more work exists, next pulse (5 min) picks it up.
- NEVER dispatch to a busy workspace — the scheduler rejects it anyway.
- Under 90 seconds wall-clock per pulse. If you're still thinking at 60s, pick the
  single highest-priority item, dispatch, and stop.
- If every agent is idle AND the backlog is empty → write "orchestrator-clean HH:MM"
  to memory and stop. Do NOT fabricate busy work.
