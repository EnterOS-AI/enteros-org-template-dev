# Secrets Matrix — Per-Role Least Privilege

The platform resolves template-declared per-workspace environment values and
stores workspace secrets encrypted. Each role gets only the credentials it
needs; this document describes capability classes, not a bundle to copy.

**Resolution order for template channel values:** per-workspace `<role>/.env`
overrides org-root `.env`, then the platform environment. These files are an
import surface for declared workspace integrations, never a production
credential cache, and must not be committed.

---

## Matrix

| Role | Secrets it gets | Scope of action enabled |
|---|---|---|
| **All workspaces** | No shared provider token is assumed. Platform-managed model auth uses the platform token flow; BYOK values are supplied only when the selected runtime/model declares them. | Run the selected runtime without distributing an org-wide credential. |
| **PM** | Optional `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (CEO comms only) | Supply channel credentials only after a nonempty literal user-ID allowlist is configured and the channel is explicitly enabled. |
| **Dev Lead, Core Lead, App Lead, CP Lead, Infra Lead, SDK Lead** | Persona-scoped `GITEA_TOKEN` with the repository permissions their role requires | Review and merge only within the team's repository and approval policy. |
| **Triage Operator** | Persona-scoped `GITEA_TOKEN` for the repositories assigned to triage | Close stale work, label, and escalate. Mechanical merges still follow repository policy. |
| **Engineers** (Backend, Frontend, Full-stack, DevOps, Platform, SRE, etc.) | Persona-scoped `GITEA_TOKEN` with PR-author/comment permissions | Raise PRs and respond to review comments. No implicit merge authority. |
| **QA Engineer** | Persona-scoped `GITEA_TOKEN` with review/comment permissions | Run tests and post evidence-backed review outcomes. |
| **Security Auditor, Offensive Security Engineer** | Persona-scoped `GITEA_TOKEN` with review/comment permissions | Post evidence-backed security review outcomes. |
| **UIUX Designer** | Persona-scoped `GITEA_TOKEN` with review/comment permissions | Post evidence-backed UI/UX review outcomes. |
| **Marketing Lead** | `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_ORG_ID`, `X_API_KEY`, `X_API_SECRET`, `X_BEARER_TOKEN`, `BUFFER_API_KEY`, `MAILCHIMP_API_KEY` | Publish content to social channels. Sole publisher. |
| **Content Marketer, Social Media Brand, SEO Analyst** | Persona-scoped `GITEA_TOKEN`; no publishing keys | Draft content through internal/public PR review. Marketing Lead controls publication. |
| **Community Manager** | Only the native channel credentials declared for assigned community surfaces | Respond only on channels with a nonempty literal user-ID allowlist and explicit enablement; SCM write requires a separately scoped persona token. |
| **Research Lead, Market Analyst, Competitive Intelligence, Tech Researcher** | Persona-scoped `GITEA_TOKEN`; scoped search API credential when provisioned | File research issues and PRs. No merge or marketing publication authority. |
| **DevOps Engineer, SRE Engineer, Infra-Runtime-BE** | Persona-scoped `GITEA_TOKEN` plus a path-scoped Infisical identity | Fetch exactly the operational secret required for an authorized action; no standing provider-key bundle. |
| **CP-BE, CP-QA, CP-Security** (control plane) | Persona-scoped `GITEA_TOKEN` for `molecule-controlplane` | Work on provider-aware CP code. Cloud-provider support does not grant direct production credentials. |
| **Documentation Specialist, Technical Writer** | Persona-scoped `GITEA_TOKEN` for assigned documentation repositories | Documentation PRs only. |
| **Release Manager** | Persona-scoped `GITEA_TOKEN`; package-publish credentials fetched by the authorized release workflow | Tag and publish only after repository gates pass. |

---

## Why this matters

- **Prompt-injection blast radius**: an attacker who exfiltrates a workspace's secrets via prompt injection only gets that role's keys. Engineer compromise ≠ org-wide write. Marketing compromise ≠ another role's channel credential.
- **Audit trail**: when something goes wrong, the secret used identifies the role that did it.
- **Provisioning clarity**: populate only the integration values declared by
  the selected workspaces; never copy a production credential bundle.

---

## Workspace-secret setup

Use the platform's template-import secret flow. For self-hosted imports that
use `.env`, start from only the relevant role's `.env.example`, populate the
declared integration values, keep the file uncommitted and mode-restricted, and
remove it after successful import. The platform encrypts persisted workspace
secrets.

Native-channel credentials alone are not authorization. Keep a channel
disabled unless its YAML entry has a nonempty list of literal user IDs in
`allowed_users`. Omitted/empty lists are fail-open in current core, and
`${...}` references are not expanded in this field (`molecule-core#4340`).

---

## Ongoing hardening

- Periodic audits of persona-token scopes and unused identities
- Egress filtering on workspace networks — limits what an exfiltrated secret can be sent to
- Volume encryption at rest — protects `.env` in workspace volumes from backup leak
- Token issuance audit logging — answers "who fetched the org token at time X?"
