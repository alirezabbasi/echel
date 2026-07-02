---
type: component-architecture
stage: architecture
status: draft
owner: architecture
updated: 2026-07-02
---
# Component Architecture

## Purpose

Component architecture identifies the system parts that implement the architecture contexts. Components describe responsibilities and contracts, not task assignments.

## Component Register

| ID | Component | Responsibility | Source IDs | Domain Contexts | Rationale | ADR Coverage | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ARCH-201 | Product Wiki | Store product-owned memory as human-readable Markdown. | REQ-001, NFR-001, NFR-002 | BC-001, BC-206 | Markdown is inspectable by founders, domain experts, and agents without custom tooling. | ADR-0001, ADR-0004 | Existing |
| ARCH-202 | Lifecycle CLI | Provide deterministic commands for lifecycle stages, gates, graph updates, packets, and reviews. | REQ-005, REQ-006, NFR-005 | BC-001, BC-005, BC-211 | CLI keeps automation scriptable and local-first. | ADR-0002, ADR-0005 | Existing |
| ARCH-203 | Gate Engine | Evaluate readiness from product artifacts before downstream work. | REQ-003, REQ-004, NFR-003 | BC-003, BC-004, BC-209 | Gates turn methodology into executable safety checks. | ADR-0002, ADR-0005 | Existing |
| ARCH-204 | Product Graph | Connect product, requirement, domain, architecture, task, decision, risk, evidence, milestone, and release nodes. | REQ-001, NFR-002, NFR-005 | BC-001, BC-210 | Graph prevents isolated task reasoning and enables traceability. | ADR-0002 | Existing |
| ARCH-205 | Work Packet Generator | Produce agent-readable work context with acceptance and evidence obligations. | REQ-006, NFR-005 | BC-005, BC-211 | Agents need scoped, verifiable context rather than raw document dumps. | ADR-0002 | Existing |
| ARCH-206 | Review And Evidence Layer | Compare completed work against acceptance criteria and proof obligations. | REQ-004, NFR-003 | BC-004, BC-209 | Verification must be durable and auditable. | ADR-0002 | Existing |
| ARCH-207 | Local Cockpit | Provide a local product-owner control surface over memory, graph, tasks, readiness, packets, reviews, and chat. | REQ-006, NFR-001 | BC-005 | Cockpit improves steering without moving product memory out of the repo. | ADR-0004 | Existing |
| ARCH-208 | Architecture Artifact Surface | Hold architecture concern documents and downstream handoff records. | TASK-0018, ARCH-001 | BC-001, BC-003 | Architecture needs structured surfaces before generation and gates can be reliable. | ADR-0005 | New |

## Component Interactions

| From Component | Interaction | To Component | Contract | Failure Handling |
| --- | --- | --- | --- | --- |
| ARCH-202 Lifecycle CLI | reads and writes | ARCH-201 Product Wiki | Markdown artifacts and JSON registries | Refuse unsafe generation when gates fail. |
| ARCH-202 Lifecycle CLI | invokes | ARCH-203 Gate Engine | Stage name and repository config | Return blocking messages without partial downstream writes. |
| ARCH-201 Product Wiki | feeds | ARCH-204 Product Graph | Markdown, generated sections, and manual graph JSON | Graph validation reports broken references. |
| ARCH-204 Product Graph | enriches | ARCH-205 Work Packet Generator | Related nodes and edges | Missing context must be surfaced in packet output. |
| ARCH-206 Review And Evidence Layer | updates | ARCH-201 Product Wiki | Reviews, proof packs, evidence registry | Missing evidence blocks closure and release readiness. |
| ARCH-207 Local Cockpit | calls | ARCH-202 Lifecycle CLI | Safe command bridge | Unsafe commands require explicit implementation before exposure. |

## Alternatives Considered

| Option | Why Not Default | Revisit Trigger |
| --- | --- | --- |
| Hosted orchestration service | Adds deployment, tenancy, auth, and operations before the local OS is stable. | Multiple projects require shared team execution. |
| Database-first product memory | Reduces direct inspectability and makes domain experts dependent on tooling. | Query scale or collaboration requirements exceed Markdown plus graph files. |
| Single architecture document | Too thin for gates, ADR coverage, and downstream repository generation. | Only acceptable as a generated summary of the expanded model. |

## Handoff Requirements

- TASK-0019 should generate architecture content into these component rows or generated sections.
- TASK-0020 should validate that every major component has source IDs, rationale, ADR coverage when needed, and domain context mappings.
- Repository factory tasks must not create code modules that lack a mapped architecture component.
