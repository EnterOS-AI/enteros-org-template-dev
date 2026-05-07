IMPORTANT: Check Molecule-AI/internal repo for roadmap (PLAN.md), known issues, runbooks before starting work.

Independent work cycle for molecule-tenant-proxy + molecule-ai-workspace-runtime. Find work, write code, push, open PR, return to staging. FULL CYCLE REQUIRED.

STEP 1 — CHECK CURRENT STATE:
  cd /workspace/repo
  If NOT on staging: push previous work first.
    git fetch origin staging && git rebase origin/staging
    git push origin $(git branch --show-current)
    tea pr create --base staging --title "fix: description" --body "description" 2>/dev/null || true
    git checkout staging && git pull origin staging

STEP 2 — FIND WORK:
  tea issue list --repo molecule-ai/molecule-tenant-proxy --state open --json number,title,labels,assignees --jq '.[] | select(.assignees | length == 0) | "#\(.number) \(.title)"'
  tea issue list --repo molecule-ai/molecule-ai-workspace-runtime --state open --json number,title,labels,assignees --jq '.[] | select(.assignees | length == 0) | "#\(.number) \(.title)"'

STEP 3 — SELF-ASSIGN:
  tea issue edit <NUMBER> --repo molecule-ai/<repo> --add-assignee @me

STEP 4 — WRITE CODE:
  git checkout -b fix/issue-N-description
  Write code. Run tests.
  git add && git commit -m "fix(proxy): description (closes #N)"

STEP 5 — PUSH + OPEN PR:
  git fetch origin staging && git rebase origin/staging
  git push origin <branch>
  tea pr create --base staging --title "fix: description" --body "Closes #N"

STEP 6 — RETURN TO STAGING:
  git checkout staging && git pull origin staging
  MANDATORY. Do not stay on feature branch.

RULES: All PRs target staging. Rebase before push. Merge-commits only.
