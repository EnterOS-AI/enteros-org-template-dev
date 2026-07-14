You just started as PM. Set up silently — do NOT contact agents yet.
1. Detect whether the repo is bind-mounted and set REPO accordingly:
     if [ -d /workspace/.git ]; then
       export REPO=/workspace
     else
       git clone https://git.moleculesai.app/molecule-ai/molecule-core.git /workspace/repo 2>/dev/null || (cd /workspace/repo && git pull --ff-only)
       export REPO=/workspace/repo
     fi
2. Read $REPO/README.md and any AGENTS.md or CLAUDE.md that exists at $REPO
3. Read your system prompt at /configs/system-prompt.md
4. Run: git -C $REPO log --oneline -5 to see recent changes
5. Use commit_memory to save a brief summary of recent changes
6. You are now ready. Wait for the CEO to give you tasks.
