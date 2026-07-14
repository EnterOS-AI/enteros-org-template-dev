IMPORTANT: Check molecule-ai/internal repo for roadmap (PLAN.md), known issues, runbooks before starting work.

Refresh the topic backlog from recent signals.

1. Pull the ten newest merged Gitea PRs from the owning repositories via their
   `/pulls?state=closed` API and filter for non-null `merged_at`
   + `molecule-core/docs/ecosystem-watch.md` last-week entries at current Gitea `main`
   + competitor blog feeds (Hermes, Letta, n8n — use the current private
     positioning source located through `molecule-ai/internal` search)
2. Rank candidates: technical-deep-dive vs positioning-story, target keyword pull.
3. MULTIMEDIA — for published articles, consider audio supplements:
   - TTS: Generate audio versions of blog posts for podcast-style consumption.
   - Music: Create background music for tutorial walkthroughs and video content.
   When publishing, produce a TTS audio version alongside the written content.
4. Save top 5 to memory 'research-backlog:content-marketer'.
4. Route audit_summary to PM (category=content).
5. If 5+ already queued, PM-message "clean: backlog full".
