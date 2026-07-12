---
type: validation
status: draft
stage: validation
---
# Security Tests

## Purpose

Security tests verify that Echel's product memory, generated repository baseline, command bridge, configuration, and release workflow do not create avoidable security risk.

## Security Test Matrix

| Test ID | Security Concern | Requirement IDs | Task IDs | Domain IDs | Acceptance Criteria | Validation Method | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TEST-SEC-001 | Configuration and secret handling are documented and not committed. | NFR-003, NFR-004 | TASK-0024, TASK-0025, TASK-0035 | DM-006, BC-003 | AC-003 | Inspect `.env.example`, generated docs, and future deployment secrets docs. | Planned |
| TEST-SEC-002 | Cockpit command bridge uses allowlisted commands only. | NFR-003, REQ-006 | TASK-0043, TASK-1017 | DM-005, BC-003 | AC-006 | Review command bridge policy and run cockpit command tests when available. | Planned |
| TEST-SEC-003 | Architecture security model exists before release. | NFR-003, REQ-003 | TASK-0018, TASK-0020, TASK-0036 | DM-006, BC-201 | AC-004 | Run `python3 tools/echel.py readiness --stage architecture` and release gate once implemented. | Planned |
| TEST-SEC-004 | Evidence and validation records are tamper-aware. | NFR-002, NFR-003 | TASK-0033, TASK-0034 | DM-012, DM-006 | AC-007, AC-003 | Register proof through `python3 tools/echel.py evidence add` and verify checksum-backed records. | Planned |

## Security Blockers

| Blocker ID | Description | Owner Task | Status |
| --- | --- | --- | --- |
| SEC-BLOCK-001 | Deployment and release gates are not yet implemented. | TASK-0035, TASK-0036 | Open |
