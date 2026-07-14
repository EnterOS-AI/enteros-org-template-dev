# template-molecule-dev

Molecule AI org template defining a full organizational hierarchy of agent workspaces.

## Usage

### In Molecule AI canvas
Select this template from the "Org Templates" section when setting up a new organization.

The canonical source is the
[`molecule-ai/molecule-ai-org-template-molecule-dev`](https://git.moleculesai.app/molecule-ai/molecule-ai-org-template-molecule-dev)
repository on Molecule's Gitea instance. Import it through the canvas template
catalog; this repository does not document a separate URL-install scheme.

## Structure
- `org.yaml` — full org definition (workspaces, roles, plugins, schedules, channels)
- Per-role directories contain `system-prompt.md` files for each workspace role.

## Schema version
`template_schema_version: 1` — validated against the current org-template
schema in CI.

## Native-channel safety

Checked-in local Telegram/Discord declarations remain disabled unless they
carry a nonempty literal `allowed_users` list. Current core treats an omitted
or empty list as fail-open, and environment references in `allowed_users` are
not expanded (`molecule-core#4340`).

The pinned external dev department at `v1.0.0` still contains four affected
channel declarations. Its fix is under review in `molecule-dev-department#15`;
an owner-approved release and exact-tag repin are tracked in
`molecule-ai/internal#1009`. Until that repin lands, do not describe the fully
composed template as channel-safe.

## License
Business Source License 1.1 — © Molecule AI.
