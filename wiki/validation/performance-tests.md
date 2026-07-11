---
type: validation
status: draft
stage: validation
---
# Performance Tests

## Purpose

Performance tests ensure that Echel remains usable as product memory grows and that generated repository baselines keep a fast local feedback loop.

## Performance Test Matrix

| Test ID | Performance Concern | Requirement IDs | Task IDs | Domain IDs | Acceptance Criteria | Validation Method | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TEST-PERF-001 | Core unit and lifecycle regression suite remains fast enough for one-session agent work. | NFR-001, REQ-006 | TASK-0013..TASK-0033 | DM-005, BC-003 | AC-006 | Time `python3 -m unittest discover -s tests` during validation reporting. | Planned |
| TEST-PERF-002 | Wiki health remains fast enough for documentation synchronization. | NFR-001, NFR-002 | TASK-0021..TASK-0032 | DM-012, BC-001 | AC-007 | Time `make wiki-health` during validation reporting. | Planned |
| TEST-PERF-003 | Graph build and traceability generation remain practical as lifecycle nodes grow. | NFR-002, NFR-005 | TASK-0029, TASK-0030, TASK-0031 | DM-012, BC-001 | AC-007 | Time `python3 tools/echel.py graph build` and `python3 tools/echel.py traceability`. | Planned |
| TEST-PERF-004 | Generated repository verification stays dependency-light. | NFR-001, REQ-004 | TASK-0024, TASK-0025, TASK-1006 | DM-005, BC-003 | AC-003, AC-006 | Run generated `scripts/verify.sh` once TASK-1006 is resumed. | Planned |

## Performance Budgets

| Budget ID | Command Or Workflow | Initial Budget | Notes |
| --- | --- | ---: | --- |
| PERF-BUDGET-001 | `python3 -m unittest discover -s tests` | 10 seconds | Local development budget for agent iteration. |
| PERF-BUDGET-002 | `make wiki-health` | 10 seconds | Documentation synchronization budget. |
| PERF-BUDGET-003 | `python3 tools/echel.py traceability` | 5 seconds | Traceability report budget before release gates consume it. |
