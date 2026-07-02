---
type: mvp-scope
stage: requirements
status: draft
owner: product
updated: 2026-07-02
---

# MVP Scope

## Purpose

MVP scope defines the smallest requirement set that can safely carry Echel from product strategy into downstream domain, architecture, planning, implementation, QA, release, and operations work.

## MVP Goal

Create a requirements model that preserves intent, separates delivery phases, and makes every requirement testable before automation is introduced.

## Included in MVP

| Requirement ID | Title | Why Included | Source IDs | Dependencies | Acceptance | Exit Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| REQ-001 | Preserve product intent across lifecycle artifacts | Required for AI-native memory continuity | PDS-001, CANON-001, STRAT-001 | None | AC-001 | Source IDs visible in requirement rows |
| REQ-002 | Separate MVP requirements from later scope | Required to prevent scope creep | CANON-002, STRAT-002 | REQ-001 | AC-002 | MVP and later-scope tables are separate |
| REQ-003 | Capture requirement dependencies and risks before execution | Required for planning quality | PDS-002, CANON-003 | REQ-001 | AC-003 | Dependency and risk columns are populated |
| REQ-004 | Link requirements to acceptance criteria | Required for QA and release readiness | CANON-004, STRAT-003 | REQ-001 | AC-004 | Every MVP row links to `AC-###` |
| NFR-001 | Keep requirement artifacts plain Markdown | Required for domain-expert review | CANON-001, STRAT-001 | None | AC-006 | Files can be read without custom tooling |
| NFR-002 | Keep requirement IDs stable | Required for downstream traceability | TRACE-001, CANON-002 | REQ-001 | AC-007 | IDs are not reused after reference |
| NFR-003 | Require objective verification methods | Required for testability | CANON-004, STRAT-003 | REQ-004 | AC-008 | Each MVP requirement has a verification method |
| NFR-004 | Separate requirements into dedicated views | Required for maintainability | CANON-005, TRACE-001 | None | AC-009 | Six requirement documents exist |

## Deferred From MVP

| Requirement ID | Phase | Deferred Because | Planned Follow-Up |
| --- | --- | --- | --- |
| REQ-005 | V1 | Model must exist before CLI automation | TASK-0013 |
| REQ-006 | V1 | Agent-consumable parsing belongs with command implementation | TASK-0013 |
| NFR-005 | V1 | Parser constraints should be validated by implementation | TASK-0013 and TASK-0014 |

## MVP Exit Criteria

- [ ] Requirement model documents exist under `wiki/requirements/`.
- [ ] MVP and deferred scope are visibly separated.
- [ ] Every MVP requirement has source IDs.
- [ ] Every MVP requirement has acceptance criteria.
- [ ] Every MVP requirement has dependencies, risks, and verification method.
- [ ] Deferred automation work is linked to future tasks.
