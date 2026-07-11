---
type: validation
status: draft
stage: validation
---
# Acceptance Tests

## Purpose

Acceptance tests prove that user-visible and owner-visible Echel behaviors satisfy explicit requirements and acceptance criteria.

## Acceptance Test Matrix

| Test ID | Scenario | Requirement IDs | Acceptance Criteria | Task IDs | Domain IDs | Validation Method | Current Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TEST-ACC-001 | Requirement artifacts preserve source IDs and acceptance criteria. | REQ-001, REQ-005, NFR-002 | AC-001, AC-005, AC-007 | TASK-0012, TASK-0013, TASK-0014 | DM-012, BC-001 | Inspect requirement tables and run `python3 tools/echel.py readiness --stage requirements`. | Planned |
| TEST-ACC-002 | Domain and architecture remain gated before execution planning. | REQ-003, REQ-005 | AC-004, AC-005 | TASK-0017, TASK-0020, TASK-0021 | DM-201, BC-201, BC-210 | Run `python3 tools/echel.py readiness --stage domain` and `python3 tools/echel.py readiness --stage architecture`. | Planned |
| TEST-ACC-003 | Agent task packets include scope, validation, rollback, docs, and DoD. | REQ-004, REQ-006 | AC-003, AC-006 | TASK-0023, TASK-1001, TASK-1002 | DM-005, BC-003 | Inspect generated `wiki/work/TASK-1xxx-*.md` files and `TASK_INDEX`. | Planned |
| TEST-ACC-004 | Traceability matrix shows lifecycle coverage and broken links. | REQ-001, NFR-002, NFR-005 | AC-001, AC-007 | TASK-0031, TASK-1010 | DM-012, BC-001 | Run `python3 tools/echel.py traceability` and inspect `wiki/reports/traceability-matrix.md`. | Planned |
| TEST-ACC-005 | Generated repository baseline remains locally verifiable. | REQ-004, REQ-006, NFR-001 | AC-003, AC-006 | TASK-0024, TASK-0025, TASK-1006 | DM-005, BC-003 | Run generated repository verification commands once TASK-1006 is resumed. | Planned |

## Acceptance Rules

- A test cannot be marked passing unless its requirement IDs, task IDs, domain IDs, and acceptance criteria remain present.
- A failed acceptance test must create or update a task, risk, contradiction, or blocker.
- A skipped acceptance test must state the reason and the future task responsible for closing it.

## Current Blockers

| Blocker ID | Description | Affected Tests | Owner Task | Status |
| --- | --- | --- | --- | --- |
| VAL-BLOCK-001 | Evidence registration is not yet automated. | TEST-ACC-004, TEST-ACC-005 | TASK-0034 / TASK-1013 | Open |
| VAL-BLOCK-002 | Full validation command is not implemented yet. | All acceptance tests | TASK-0033 / TASK-1012 | Open |
