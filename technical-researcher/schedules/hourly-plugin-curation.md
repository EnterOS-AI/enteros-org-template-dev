IMPORTANT: Check molecule-ai/internal repo for roadmap (PLAN.md), known issues, runbooks before starting work.

Weekly survey of current `molecule-ai-plugin-*` and
`molecule-ai-workspace-template-*` Gitea repositories for evolution
opportunities. The team should keep gaining capabilities.

1. Inventory:
   - Enumerate the Gitea organization with pagination; select current plugin and workspace-template repositories.
   - Read each selected repository's manifest and current default-branch source.
   - Read `molecule-ai-org-template-molecule-dev/org.yaml` to see how plugins are wired.
2. Gap analysis:
   - Any documented runtime capability not exposed through the current plugin surface?
   - Any role with no plugins beyond defaults that *should* have extras?
   - Any plugin that's installed everywhere via defaults but is rarely used?
3. External survey (use browser-automation):
   - github.com/topics/ai-agents (last week)
   - github.com/topics/mcp-server (last week)
   - claude.ai/cookbook, openai/swarm releases
   - anthropic blog, openai blog, langchain blog (last week)
4. For 1-3 highest-value findings, file a Gitea issue with a concrete proposal:
   - "Plugin proposal: <name> — wraps <upstream tool> for <role(s)>"
   - body: what it does, which roles benefit, integration sketch (~30 lines),
     upstream link, license check.
5. Routing: delegate_task to PM with audit_summary metadata
   (category=plugins, issues=[…], top_recommendation=…).
6. If nothing notable this week, PM-message a one-line "clean".
