---
type: validation
status: draft
stage: validation
---
# Test Strategy

## Purpose

This document defines how Echel proves that product memory, generated repository behavior, lifecycle commands, and AI-agent handoffs remain trustworthy before release.

## Source Inputs

- Requirements: [[../requirements/product-requirements]], [[../requirements/functional-requirements]], [[../requirements/non-functional-requirements]], [[../requirements/acceptance-criteria]]
- Domain model: [[../domain/domain-overview]], [[../domain/ubiquitous-language]], [[../domain/policies-and-rules]]
- Architecture: [[../architecture/overview]], [[../architecture/component-architecture]], [[../architecture/security-architecture]], [[../architecture/observability-architecture]]
- Execution tasks: [[../work/TASK_INDEX]]
- Traceability report: [[../reports/traceability-matrix]]

## Validation Principles

- Every validation item must map to at least one requirement ID.
- Every implementation-facing validation item must map to at least one task ID.
- Every product behavior validation item must map to at least one domain concept or bounded context.
- Every requirement validation item must map to an acceptance criterion ID.
- Validation status must be explicit: `Planned`, `Passing`, `Failing`, `Skipped`, or `Blocked`.
- Skipped or blocked validation must include a reason and owner.

## Validation Levels

| Level | Purpose | Primary Artifact | Required Before |
| --- | --- | --- | --- |
| Acceptance | Prove requirements and acceptance criteria are satisfied. | [[acceptance-tests]] | Release readiness |
| Integration | Prove lifecycle commands and generated repository surfaces work together. | [[integration-tests]] | Validation command |
| E2E | Prove owner workflows cross lifecycle stages safely. | [[e2e-tests]] | Release readiness |
| Security | Prove security-critical behavior and docs are not bypassed. | [[security-tests]] | Release readiness |
| Performance | Prove local and generated workflows stay usable. | [[performance-tests]] | Release readiness |
| Validation report | Summarize pass/fail/skipped/blocker state. | [[validation-report]] | Release gate |

## Traceability Map

| Validation ID | Scope | Requirement IDs | Task IDs | Domain IDs | Acceptance Criteria | Evidence Target | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TEST-001 | Requirements traceability and acceptance coverage | REQ-001, NFR-002 | TASK-0013, TASK-0014, TASK-1011 | DM-012, BC-001 | AC-001, AC-007 | EVID-VALIDATION-001 | Planned |
| TEST-002 | Architecture, domain, and graph consistency | REQ-003, REQ-005, NFR-002 | TASK-0017, TASK-0020, TASK-0030 | DM-201, BC-201 | AC-004, AC-005 | EVID-VALIDATION-002 | Planned |
| TEST-003 | Agent-executable task and generated repository baseline | REQ-004, REQ-006, NFR-001 | TASK-0023, TASK-0024, TASK-0025 | DM-005, BC-003 | AC-003, AC-006 | EVID-VALIDATION-003 | Planned |
| TEST-004 | Traceability matrix and broken-chain visibility | REQ-001, NFR-002, NFR-005 | TASK-0031, TASK-1010, TASK-1011 | DM-012, BC-001 | AC-001, AC-007 | EVID-VALIDATION-004 | Planned |
| TEST-005 | Validation and evidence lifecycle readiness | REQ-004, NFR-003 | TASK-1011, TASK-1012, TASK-1013 | DM-006, BC-003 | AC-003 | EVID-VALIDATION-005 | Planned |

## Required Commands

| Command | Purpose | Expected Result | Evidence Target |
| --- | --- | --- | --- |
| `python3 -m unittest discover -s tests` | Unit and lifecycle regression coverage. | Passing tests or explicit failures. | EVID-VALIDATION-UNIT |
| `python3 tools/echel.py graph validate` | Graph integrity and metadata validation. | Pass or explicit graph issues. | EVID-VALIDATION-GRAPH |
| `python3 tools/echel.py traceability` | Traceability matrix regeneration. | Report exists with broken-chain notes. | EVID-VALIDATION-TRACE |
| `make wiki-health` | Documentation health, index, and governance checks. | 0 wiki health issues. | EVID-VALIDATION-WIKI |
| `python3 tools/echel.py doctor` | Full gate surface. | Pass or known accepted blockers. | EVID-VALIDATION-DOCTOR |

## Handoff To Validation Command

TASK-0033 / TASK-1012 should consume these artifacts, summarize each validation ID, and write a machine-readable or report-backed pass/fail/skipped/blocker view without redefining the validation model.
