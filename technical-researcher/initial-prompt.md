You just started. Set up your environment silently — do NOT contact other agents yet.

1. Clone your assigned repos:
   mkdir -p /workspace/repos
   git clone "https://git.moleculesai.app/molecule-ai/molecule-core.git" /workspace/repos/molecule-core 2>/dev/null || (cd /workspace/repos/molecule-core && git pull --ff-only)
   ln -sfn /workspace/repos/molecule-core /workspace/repo

2. Read /workspace/repos/molecule-core/README.md and any root AGENTS.md or CLAUDE.md that exists in the current checkout
3. Read your role: cat /configs/system-prompt.md
4. Check internal roadmap: git clone https://git.moleculesai.app/molecule-ai/internal.git /tmp/internal 2>/dev/null || (cd /tmp/internal && git pull --ff-only); sed -n '1,100p' /tmp/internal/PLAN.md
5. Save key conventions to memory.
6. Wait for tasks from your parent — do not initiate contact.
