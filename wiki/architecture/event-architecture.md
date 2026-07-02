---
type: event-architecture
stage: architecture
status: draft
owner: architecture
updated: 2026-07-02
---
# Event Architecture

## Purpose

Event architecture defines lifecycle events that matter to product memory, graph updates, gates, reviews, and operations. These are product and system events, not message-broker commitments.

## Event Register

| ID | Event | Meaning | Producer | Consumer | Source IDs | Rationale | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ARCH-501 | Discovery Field Updated | A PDS field changed and downstream truth may need review. | `echel discover` | Canon drift, strategy, requirements | REQ-001, NFR-002 | Upstream changes must not silently invalidate downstream artifacts. | Existing |
| ARCH-502 | Canon Drift Detected | Discovery and canon disagree. | `echel canon-drift` | Product owner, memory records, canon stale markers | REQ-003, NFR-002 | Contradictions must become durable product memory. | Existing |
| ARCH-503 | Requirements Generated | Requirements were derived from canon and strategy. | `echel requirements` | Requirements gate, domain command, graph | REQ-001, REQ-005 | Domain work needs stable requirement rows. | Existing |
| ARCH-504 | Domain Generated | Domain rows and graph mappings were refreshed from requirements. | `echel domain` | Domain gate, architecture stage | REQ-001, REQ-006 | Architecture must preserve generated and authored domain mappings. | Existing |
| ARCH-505 | Stage Gate Evaluated | A stage readiness gate passed or blocked. | Gate engine | CLI, cockpit, logs, downstream commands | REQ-003, REQ-004, NFR-003 | Gate results are execution safety signals. | Existing |
| ARCH-506 | Work Packet Generated | Agent build context was prepared. | Work packet generator | Implementation agent, review layer | REQ-006, NFR-005 | Agent context must be reproducible and reviewable. | Existing |
| ARCH-507 | Evidence Registered Or Validated | A verification artifact was linked or checked. | Evidence layer | Close-task, readiness, proof packs | REQ-004, NFR-003 | Completed work needs proof, not only status text. | Existing |
| ARCH-508 | Architecture Artifact Expanded | The architecture model gained structured concern documents. | TASK-0018 | Future architecture command and gate | ARCH-001, ADR-0005 | Architecture needs deterministic surfaces before automation. | New |

## Event Handling Rules

- Events are recorded through durable artifacts such as `wiki/log.md`, reports, memory records, generated sections, graph files, or evidence registries.
- No external event broker is required for the current architecture.
- If event volume or collaboration requirements grow, introduce an ADR before adding a broker, queue, or hosted event service.
- Events that affect product truth must be recoverable from committed project memory.

## Domain Event Alignment

| Domain Event | Architecture Event | Preservation Rule |
| --- | --- | --- |
| DE-001 Requirement Intent Preserved | ARCH-503 Requirements Generated | Requirement source IDs must survive generation. |
| DE-003 Scope Boundary Changed | ARCH-505 Stage Gate Evaluated | Scope changes must affect readiness before planning. |
| DE-004 Acceptance Criterion Linked | ARCH-507 Evidence Registered Or Validated | Evidence expectations must trace to acceptance criteria. |
| DE-005 Agent Context Prepared | ARCH-506 Work Packet Generated | Work packets must cite gated requirement, domain, and architecture context. |

## Failure Handling

| Failure | Handling | Recovery |
| --- | --- | --- |
| Generated artifact is stale | Gate blocks or drift report marks stale section. | Regenerate from upstream source or record owner decision. |
| Event has no durable trace | Treat as operational-only until promoted. | Add log, report, evidence, or decision artifact. |
| Event changes architecture choice | Create or update an ADR before downstream roadmap work. | Re-run affected gates and graph validation. |
