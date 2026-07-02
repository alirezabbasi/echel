---
type: architecture-overview
stage: architecture
status: draft
owner: architecture
updated: 2026-07-02
---
# Architecture Overview

## Purpose

This document is the architecture stage entry point. It turns the gated domain model into technical structure without changing product intent, requirement meaning, or domain boundaries.

Architecture work may start only after:

- `echel readiness --stage requirements` passes;
- `echel readiness --stage domain` passes;
- architecture choices reference requirement IDs, domain IDs, and ADRs where needed.

## Source Inputs

- Requirements: [[../requirements/product-requirements]], [[../requirements/functional-requirements]], [[../requirements/non-functional-requirements]]
- Domain model: [[../domain/domain-overview]], [[../domain/bounded-contexts]], [[../domain/ubiquitous-language]], [[../domain/policies-and-rules]]
- Lifecycle schema: `schema/lifecycle-stage.schema.md`
- Traceability schema: `schema/traceability.schema.md`
- Architecture decision: [[../decisions/ADR-0005-adopt-vnext-architecture-artifact-model]]

## System Shape

| ID | Choice | Rationale | Source IDs | Domain Boundaries Preserved | ADR Coverage | Status |
| --- | --- | --- | --- | --- | --- | --- |
| ARCH-001 | Product-owned Markdown memory with Echel runtime tooling | Markdown keeps project memory inspectable by domain experts and AI agents while tooling can validate and transform it. | REQ-001, NFR-001, NFR-002 | BC-001, BC-206, BC-207 | ADR-0001, ADR-0004 | Accepted |
| ARCH-002 | Lifecycle command surface over staged product artifacts | Commands make discovery, canon, strategy, requirements, domain, architecture, execution, validation, release, and operations repeatable. | REQ-005, REQ-006, NFR-005 | BC-001, BC-205, BC-210, BC-211 | ADR-0002, ADR-0005 | Accepted |
| ARCH-003 | Deterministic gates before downstream generation | Gates prevent agents from treating incomplete or inconsistent artifacts as ready product truth. | REQ-003, REQ-004, NFR-003 | BC-003, BC-004, BC-209 | ADR-0002, ADR-0005 | Accepted |
| ARCH-004 | Local-first cockpit and CLI orchestration | Product owners need an inspectable control surface without requiring hosted infrastructure. | REQ-006, NFR-001, NFR-005 | BC-005, BC-211 | ADR-0004 | Accepted |

## Major Decision Coverage

| Decision Area | Architecture Choice | Rationale Present | ADR Required | ADR Status | Rollback Strategy |
| --- | --- | --- | --- | --- | --- |
| Product memory ownership | `wiki/` belongs to the product repository; Echel runtime may live in `echel-core/`. | Yes | Yes | ADR-0004 | Keep `WIKI_ROOT` configurable and move framework files without moving product memory. |
| Architecture artifact surface | Split architecture into dedicated concern documents. | Yes | Yes | ADR-0005 | Collapse generated views back into `wiki/architecture.md` only if deterministic gates cannot use the expanded model. |
| Gate-first lifecycle | Use stage gates before downstream generation. | Yes | Yes | ADR-0002, ADR-0005 | Allow explicit `--force` only on commands that record bypass risk. |
| Local command orchestration | Prefer CLI and local cockpit control over hosted orchestration. | Yes | Future if hosted runtime becomes required | Covered by ADR-0004 for local ownership | Keep command behavior available without cockpit. |

## Architecture Artifact Map

| Artifact | Responsibility | Primary Consumers | Must Preserve |
| --- | --- | --- | --- |
| [[context-map]] | Map domain bounded contexts to architecture contexts and integration boundaries. | Architecture gate, roadmap, task planning | BC-### ownership and forbidden responsibilities |
| [[component-architecture]] | Define runtime and tool components. | Repository factory, task generation | Requirement and domain traceability |
| [[data-architecture]] | Define product-memory, graph, evidence, and runtime data stores. | Repository factory, validation, operations | Source IDs, stable identifiers, human readability |
| [[api-architecture]] | Define command and cockpit interaction contracts. | CLI, cockpit, future agent integrations | Gate decisions and product memory ownership |
| [[event-architecture]] | Define durable lifecycle events and graph update signals. | Memory, graph, operations | Domain event semantics |
| [[workflow-architecture]] | Define system workflows from idea to verified work. | Roadmap, execution planning, QA | Lifecycle ordering and gate semantics |
| [[security-architecture]] | Define local trust boundaries, command safety, and secret handling. | QA, release, operations | Domain and product-memory integrity |
| [[observability-architecture]] | Define logs, reports, health checks, and evidence surfaces. | Operations, governance, release | Verifiable state and proof packs |

## Complexity Guardrail

Echel should remain a local-first engineering operating system until requirements or deployment evidence prove a hosted or distributed architecture is necessary.

| Complexity Choice | Default Position | Escalation Trigger | Required Evidence |
| --- | --- | --- | --- |
| Distributed services | Avoid for MVP architecture. | Multiple independently deployed product surfaces are required. | ADR plus operational runbook. |
| External databases | Avoid unless runtime state needs query performance beyond local files or SQLite. | Cockpit or multi-agent state needs concurrent access. | ADR plus backup and migration plan. |
| Remote orchestration | Avoid unless local commands cannot support required workflows. | Team, permission, or integration needs exceed local runtime. | ADR plus security review. |

## Handoff To Roadmap

Roadmap work may start only after architecture artifacts identify:

- system shape;
- component boundaries;
- data ownership;
- command or API contracts;
- security model;
- observability model;
- ADR coverage for major choices;
- traceability from requirements and domain contexts.

## Generated by `echel architecture`
This section is generated from gated domain coverage. Manual architecture judgment should be preserved outside this generated block or recorded as ADRs.

| ID | Choice | Rationale | Source IDs | Domain Boundaries Preserved | ADR Suggestion | Status |
| --- | --- | --- | --- | --- | --- | --- |
| ARCH-901 | Preserve NFR-001 through BC-201 quality architecture | `NFR-001` is already covered by DM-201, BC-201, AGG-201, DE-201, and BR-201; architecture must preserve that boundary instead of inventing a new one. | NFR-001 | DM-201, BC-201, AGG-201, DE-201, BR-201 | ADR suggested if this mapping introduces a new component, data store, integration boundary, security boundary, or deployment model. | Generated |
| ARCH-902 | Preserve NFR-002 through BC-202 quality architecture | `NFR-002` is already covered by DM-202, BC-202, AGG-202, DE-202, and BR-202; architecture must preserve that boundary instead of inventing a new one. | NFR-002 | DM-202, BC-202, AGG-202, DE-202, BR-202 | ADR suggested if this mapping introduces a new component, data store, integration boundary, security boundary, or deployment model. | Generated |
| ARCH-903 | Preserve NFR-003 through BC-203 quality architecture | `NFR-003` is already covered by DM-203, BC-203, AGG-203, DE-203, and BR-203; architecture must preserve that boundary instead of inventing a new one. | NFR-003 | DM-203, BC-203, AGG-203, DE-203, BR-203 | ADR suggested if this mapping introduces a new component, data store, integration boundary, security boundary, or deployment model. | Generated |
| ARCH-904 | Preserve NFR-004 through BC-204 quality architecture | `NFR-004` is already covered by DM-204, BC-204, AGG-204, DE-204, and BR-204; architecture must preserve that boundary instead of inventing a new one. | NFR-004 | DM-204, BC-204, AGG-204, DE-204, BR-204 | ADR suggested if this mapping introduces a new component, data store, integration boundary, security boundary, or deployment model. | Generated |
| ARCH-905 | Preserve NFR-005 through BC-205 quality architecture | `NFR-005` is already covered by DM-205, BC-205, AGG-205, DE-205, and BR-205; architecture must preserve that boundary instead of inventing a new one. | NFR-005 | DM-205, BC-205, AGG-205, DE-205, BR-205 | ADR suggested if this mapping introduces a new component, data store, integration boundary, security boundary, or deployment model. | Generated |
| ARCH-906 | Preserve REQ-001 through BC-206 product architecture | `REQ-001` is already covered by DM-206, BC-206, AGG-206, DE-206, and BR-206; architecture must preserve that boundary instead of inventing a new one. | REQ-001 | DM-206, BC-206, AGG-206, DE-206, BR-206 | ADR suggested if this mapping introduces a new component, data store, integration boundary, security boundary, or deployment model. | Generated |
| ARCH-907 | Preserve REQ-002 through BC-207 product architecture | `REQ-002` is already covered by DM-207, BC-207, AGG-207, DE-207, and BR-207; architecture must preserve that boundary instead of inventing a new one. | REQ-002 | DM-207, BC-207, AGG-207, DE-207, BR-207 | ADR suggested if this mapping introduces a new component, data store, integration boundary, security boundary, or deployment model. | Generated |
| ARCH-908 | Preserve REQ-003 through BC-208 product architecture | `REQ-003` is already covered by DM-208, BC-208, AGG-208, DE-208, and BR-208; architecture must preserve that boundary instead of inventing a new one. | REQ-003 | DM-208, BC-208, AGG-208, DE-208, BR-208 | ADR suggested if this mapping introduces a new component, data store, integration boundary, security boundary, or deployment model. | Generated |
| ARCH-909 | Preserve REQ-004 through BC-209 product architecture | `REQ-004` is already covered by DM-209, BC-209, AGG-209, DE-209, and BR-209; architecture must preserve that boundary instead of inventing a new one. | REQ-004 | DM-209, BC-209, AGG-209, DE-209, BR-209 | ADR suggested if this mapping introduces a new component, data store, integration boundary, security boundary, or deployment model. | Generated |
| ARCH-910 | Preserve REQ-005 through BC-210 product architecture | `REQ-005` is already covered by DM-210, BC-210, AGG-210, DE-210, and BR-210; architecture must preserve that boundary instead of inventing a new one. | REQ-005 | DM-210, BC-210, AGG-210, DE-210, BR-210 | ADR suggested if this mapping introduces a new component, data store, integration boundary, security boundary, or deployment model. | Generated |
| ARCH-911 | Preserve REQ-006 through BC-211 product architecture | `REQ-006` is already covered by DM-211, BC-211, AGG-211, DE-211, and BR-211; architecture must preserve that boundary instead of inventing a new one. | REQ-006 | DM-211, BC-211, AGG-211, DE-211, BR-211 | ADR suggested if this mapping introduces a new component, data store, integration boundary, security boundary, or deployment model. | Generated |
