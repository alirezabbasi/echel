---
type: data-architecture
stage: architecture
status: draft
owner: architecture
updated: 2026-07-02
---
# Data Architecture

## Purpose

Data architecture defines where product memory, graph data, runtime state, evidence, and logs live. It must preserve source IDs and human-readable project memory.

## Data Stores

| ID | Store | Owned Data | Format | Source IDs | Rationale | Backup Or Recovery | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ARCH-301 | Product Wiki Store | Canon, strategy, requirements, domain, architecture, roadmap, work, reports, decisions, logs | Markdown | REQ-001, NFR-001, NFR-002 | Product memory must be readable and committed with the project. | Git history and committed files | Existing |
| ARCH-302 | Manual Graph Store | Human and command-authored graph nodes and edges | JSON | REQ-001, NFR-002, NFR-005 | Manual graph data preserves traceability not extractable from Markdown alone. | Git history and graph rebuild | Existing |
| ARCH-303 | Generated Graph Store | Derived graph snapshot for traversal and reports | JSON | REQ-001, NFR-002 | Generated graph supports status, packets, reviews, and cockpit views. | Rebuild from wiki and manual graph | Existing |
| ARCH-304 | Evidence Registry | Evidence artifact IDs, paths, commands, and validation metadata | JSON | REQ-004, NFR-003 | Evidence needs deterministic lookup during closure and release readiness. | Git history and proof-pack references | Existing |
| ARCH-305 | Local Runtime Store | Cockpit provider configuration, chat sessions, and local command state | SQLite or local config files | REQ-006, NFR-005 | Runtime state should stay local unless a deployment requirement says otherwise. | Local export or deletion policy before release | Existing |
| ARCH-306 | Memory Record Store | Contradictions, drift findings, and durable local learning records | JSONL plus durable wiki artifacts when product-visible | REQ-003, NFR-002 | Some learning is operational; product-significant contradictions must become committed memory. | Promote important findings into wiki artifacts | Existing |

## Data Ownership Rules

- Product truth belongs in `wiki/` Markdown unless it is purely runtime state.
- Generated files must be reproducible or clearly marked as manual overrides.
- IDs such as `REQ-###`, `DM-###`, `BC-###`, `ARCH-###`, `ADR-####`, and `EVID-###` must remain stable once referenced.
- Runtime state must not be required to understand committed product memory.

## Data Flow

| Flow | From | To | Data | Validation |
| --- | --- | --- | --- | --- |
| Requirements to domain | Requirements artifacts | Domain artifacts and graph | `REQ-###`, `NFR-###`, `DM-###`, `BC-###`, `BR-###` mappings | `echel readiness --stage domain` |
| Domain to architecture | Domain artifacts | Architecture artifacts | Context boundaries, policies, workflows, events | Future `echel architecture` and architecture gate |
| Product memory to graph | Wiki and manual graph | Generated graph | Nodes and edges | `echel graph validate` |
| Work to evidence | Work packets and reviews | Evidence registry and proof packs | Verification commands, links, outcomes | Evidence validation and release readiness |

## Data Risks

| Risk | Impact | Mitigation | Owner |
| --- | --- | --- | --- |
| Generated graph drifts from wiki | Agents receive stale context. | Regenerate graph after lifecycle generation and run graph validation. | Gate Engine |
| Runtime state becomes hidden product truth | Repository memory becomes incomplete. | Promote durable product decisions, contradictions, and evidence into wiki artifacts. | Product Memory Context |
| IDs are reused for new meanings | Traceability becomes unreliable. | Supersede changed items instead of silently reusing IDs. | Product Memory Context |
