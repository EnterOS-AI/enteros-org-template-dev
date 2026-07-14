IMPORTANT: Check molecule-ai/internal repo for roadmap (PLAN.md), known issues, runbooks before starting work.

Market analysis with web search. Run every 30 minutes.

1. CHECK RESEARCH BACKLOG:
   search_memory "research-question:market-analyst"
   gitea-curl -fsS -A curl/8.4.0 \
     'https://git.moleculesai.app/api/v1/repos/molecule-ai/internal/issues?state=open&type=issues&labels=research,area:market-analyst&limit=5' | \
     python3 -c 'import json,sys; [print(item["number"],item["title"],sep="\t") for item in json.load(sys.stdin)]'

2. WEB SEARCH — gather market intelligence:
   - AI agent market sizing (analyst reports, funding rounds)
   - Enterprise AI adoption trends
   - Developer tooling market shifts
   - Pricing model evolution across AI platforms
   - Regulatory developments (EU AI Act, etc.)
   - User research signals (HN, Reddit, Discord)

3. TREND ANALYSIS:
   - Compare current signals against last cycle's snapshot
   - Identify emerging patterns (new use cases, shifting budgets)
   - Track funding rounds in AI agent space

4. ACTIONABLE INSIGHTS:
   For each finding:
   - What it means for Molecule AI
   - Recommended response (product, positioning, pricing)
   - Time sensitivity (act now vs. monitor)

5. ROUTING:
   delegate_task to Research Lead with audit_summary (category=research).
   commit_memory "market-analysis HH:MM — topics analyzed, key findings"

6. If nothing notable, Research Lead message "clean".
