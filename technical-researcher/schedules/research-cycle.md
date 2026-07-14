IMPORTANT: Check molecule-ai/internal repo for roadmap (PLAN.md), known issues, runbooks before starting work.

Research cycle with web search. Run every 30 minutes.

1. CHECK RESEARCH BACKLOG:
   search_memory "research-question:technical-researcher"
   gitea-curl -fsS -A curl/8.4.0 \
     'https://git.moleculesai.app/api/v1/repos/molecule-ai/molecule-core/issues?state=open&type=issues&labels=research,area:technical-researcher&limit=5' | \
     python3 -c 'import json,sys; [print(item["number"],item["title"],sep="\t") for item in json.load(sys.stdin)]'

2. WEB SEARCH — for active research questions, use web_search to gather current info:
   - AI agent framework releases (LangChain, AutoGen, Swarm, etc.)
   - MCP server ecosystem updates (new servers, protocol changes)
   - Claude/Anthropic SDK updates, OpenAI API changes
   - Relevant GitHub trending repos in ai-agents topic
   - Conference talks, blog posts, technical papers

3. PLUGIN CURATION (from hourly-plugin-curation):
   - Survey current plugin and workspace-template repositories on Gitea for gaps
   - External survey via web_search for new tools worth wrapping
   - File a Gitea issue for 1-3 highest-value plugin proposals

4. SYNTHESIZE findings:
   - What changed since last cycle
   - Impact on Molecule AI platform
   - Recommended actions with priority

5. ROUTING:
   delegate_task to Research Lead with audit_summary (category=plugins).
   commit_memory "tech-research HH:MM — topics researched, findings count"

6. If nothing notable, Research Lead message "clean".
