---
type: requirements
stage: requirements
status: draft
owner: product
updated: 2026-07-02
---

# Product Requirements

## Purpose

Product requirements translate validated discovery, canon, and strategy decisions into testable product outcomes. Each requirement must preserve its upstream intent so agents can plan, implement, test, and review work without losing the reason behind the requirement.

## Source Inputs

- Discovery: [[../discovery/product-discovery-spec]], [[../discovery/research-plan]], [[../discovery/assumptions]]
- Canon: [[../canon/product-canon]], [[../canon/vision]], [[../canon/product-principles]], [[../canon/non-negotiables]]
- Strategy: [[../strategy/icp]], [[../strategy/buyer-user-model]], [[../strategy/market-wedge]], [[../strategy/competitive-analysis]], [[../strategy/positioning]], [[../strategy/pricing-and-packaging]], [[../strategy/pmf-evidence]]
- Traceability contract: `schema/traceability.schema.md`

## Authoring Rules

- Use `REQ-###` for product and functional requirements.
- Use `NFR-###` only for non-functional requirements tracked in [[non-functional-requirements]].
- Every requirement must include upstream source IDs from discovery, canon, or strategy artifacts.
- Every requirement must include priority, phase, dependencies, risks, and acceptance criteria links.
- Every requirement must be testable through a stated validation method.
- Requirements without source IDs, acceptance criteria, or validation methods are not ready for planning.

## Requirement Index

| ID | Title | Type | Priority | Phase | Source IDs | Dependencies | Risks | Acceptance | Validation Method | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-001 | Preserve product intent across lifecycle artifacts | Product | P0 | MVP | PDS-001, CANON-001, STRAT-001 | None | Agents may create downstream artifacts without source context | AC-001 | Traceability review confirms downstream links exist | Draft |
| REQ-002 | Separate MVP requirements from later scope | Product | P0 | MVP | STRAT-002, CANON-002 | REQ-001 | Scope creep may weaken execution focus | AC-002 | Scope audit confirms MVP and later items are separated | Draft |
| REQ-003 | Capture requirement dependencies and risks before execution | Product | P0 | MVP | PDS-002, CANON-003 | REQ-001 | Hidden dependencies may cause blocked tasks | AC-003 | Requirement review confirms dependencies and risks are populated | Draft |
| REQ-004 | Link requirements to acceptance criteria | Product | P0 | MVP | CANON-004, STRAT-003 | REQ-001 | Untestable requirements may reach implementation | AC-004 | Every requirement has at least one linked acceptance criterion | Draft |
| REQ-005 | Support later automation through stable requirement fields | Product | P1 | V1 | TRACE-001, CANON-005 | REQ-001, REQ-004 | CLI and gate implementation may need schema changes | AC-005 | Fields align with traceability schema and planned requirements command | Draft |

## MVP Requirements

MVP requirements are the minimum set required before Echel can safely move from strategy into domain, architecture, planning, and execution work.

| Requirement ID | Included Because | Required Before | Notes |
| --- | --- | --- | --- |
| REQ-001 | Prevents intent loss across AI-generated artifacts | Domain modeling | Foundational for graph and agent memory |
| REQ-002 | Keeps initial delivery disciplined | Task planning | Prevents later-scope work from entering MVP execution |
| REQ-003 | Exposes execution blockers before tasks are created | Task planning | Supports dependency-aware work packets |
| REQ-004 | Makes every requirement testable | QA planning | Required for acceptance and proof-pack generation |

## Later Requirements

| Requirement ID | Phase | Reason Deferred | Revisit Trigger |
| --- | --- | --- | --- |
| REQ-005 | V1 | The current task defines the model; automation belongs to TASK-0013 and later gates | Start TASK-0013 |

## Readiness Checklist

- [x] All `REQ-###` rows have source IDs.
- [x] All `REQ-###` rows have priority and phase.
- [x] All `REQ-###` rows have dependencies and risks.
- [x] All `REQ-###` rows link to `AC-###` rows.
- [x] MVP and later scope are separated.
- [x] No requirement is accepted without a validation method.

## Readiness Gate

`GATE-REQUIREMENTS` evaluates this model through `echel readiness --stage requirements`. The gate parses the requirement tables directly and blocks downstream domain work when MVP `REQ-###` or `NFR-###` rows are missing source IDs, acceptance links, validation methods, dependency statements, risk statements, explicit out-of-scope records, MVP non-functional coverage, or generated requirement graph links.
