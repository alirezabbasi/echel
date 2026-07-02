---
type: acceptance-criteria
stage: requirements
status: draft
owner: product
updated: 2026-07-02
---

# Acceptance Criteria

## Purpose

Acceptance criteria turn requirements into verifiable conditions. Every criterion must identify the requirement it verifies, the expected result, the evidence needed, and the method of validation.

## Acceptance Criteria Register

| ID | Requirement IDs | Criterion | Evidence Required | Validation Method | Source IDs | Status |
| --- | --- | --- | --- | --- | --- | --- |
| AC-001 | REQ-001 | Every MVP requirement includes discovery, canon, or strategy source IDs. | Requirement rows showing populated source ID fields | Manual traceability review | PDS-001, CANON-001, STRAT-001 | Draft |
| AC-002 | REQ-002 | MVP and later-phase requirements are documented in separate sections or files. | [[mvp-scope]] and deferred-scope rows | Scope review | CANON-002, STRAT-002 | Draft |
| AC-003 | REQ-003, REQ-004 | Every MVP requirement includes dependencies and risks. | Requirement rows showing dependencies and risks | Requirement completeness review | PDS-002, PDS-003, CANON-003 | Draft |
| AC-004 | REQ-005 | Every MVP requirement links to one or more `AC-###` identifiers. | Requirement rows showing acceptance links | Acceptance mapping review | CANON-004, STRAT-003 | Draft |
| AC-005 | REQ-006, NFR-005 | Requirement fields are consistent enough for future command parsing. | Tables with stable ID, priority, phase, source, dependency, risk, acceptance, and validation columns | Schema alignment review during TASK-0013 | TRACE-001 | Draft |
| AC-006 | NFR-001 | Requirement artifacts are readable as plain Markdown without custom tooling. | Six Markdown files under `wiki/requirements/` | Manual documentation review | CANON-001, STRAT-001 | Draft |
| AC-007 | NFR-002 | Referenced requirement IDs are not reused for different meanings. | Requirement register and future traceability reports | ID stability review | TRACE-001, CANON-002 | Draft |
| AC-008 | NFR-003 | Every MVP requirement has an objective verification method. | Requirement rows showing test or review methods | Requirement quality checklist | CANON-004, STRAT-003 | Draft |
| AC-009 | NFR-004 | Product, functional, non-functional, MVP, out-of-scope, and acceptance views exist separately. | Six requirement documents | File presence and cross-reference review | CANON-005, TRACE-001 | Draft |

## Acceptance Review Rules

- Acceptance criteria must use `AC-###` IDs.
- A criterion may verify multiple related requirements when the same evidence proves them.
- A requirement may link to multiple criteria when it needs multiple proof types.
- Criteria must name evidence, not only desired behavior.
- Criteria must be reviewed before downstream task generation.

## Readiness Checklist

- [ ] Every MVP `REQ-###` has at least one acceptance criterion.
- [ ] Every MVP `NFR-###` has at least one acceptance criterion.
- [ ] Every criterion states evidence required.
- [ ] Every criterion states validation method.
- [ ] Acceptance criteria can be used by future QA and proof-pack workflows.
