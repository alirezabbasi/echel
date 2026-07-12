---
type: validation
status: draft
stage: validation
---
# Integration Tests

## Purpose

Integration tests prove that Echel lifecycle commands, graph outputs, reports, generated repository files, and product memory remain synchronized.

## Integration Matrix

| Test ID | Integration Surface | Requirement IDs | Task IDs | Domain IDs | Acceptance Criteria | Command Or Review | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TEST-INT-001 | Requirements command to requirements gate to graph nodes. | REQ-001, REQ-005, NFR-002 | TASK-0013, TASK-0014 | DM-012, BC-001 | AC-001, AC-005, AC-007 | `python3 tools/echel.py requirements --force`, `python3 tools/echel.py readiness --stage requirements`, graph review in test fixture. | Planned |
| TEST-INT-002 | Domain command to domain gate to architecture command. | REQ-003, REQ-005 | TASK-0016, TASK-0017, TASK-0019 | DM-201, BC-201, AGG-201 | AC-004, AC-005 | Domain and architecture command regression coverage. | Planned |
| TEST-INT-003 | Architecture gate to roadmap and execution tasks. | REQ-004, REQ-006 | TASK-0020, TASK-0021, TASK-0023 | DM-005, BC-003 | AC-003, AC-006 | `python3 tools/echel.py execution-tasks` after architecture readiness. | Planned |
| TEST-INT-004 | Execution tasks to repository factory output. | REQ-004, REQ-006, NFR-001 | TASK-0023, TASK-0024, TASK-0025 | DM-005, BC-003 | AC-003, AC-006 | Repository factory regression tests and generated `scripts/verify.sh`. | Planned |
| TEST-INT-005 | Graph metadata to traceability matrix. | REQ-001, NFR-002, NFR-005 | TASK-0030, TASK-0031, TASK-1011 | DM-012, BC-001 | AC-001, AC-007 | `python3 tools/echel.py graph validate` and `python3 tools/echel.py traceability`. | Planned |

## Integration Risks

| Risk ID | Risk | Mitigation | Owner Task |
| --- | --- | --- | --- |
| VAL-RISK-001 | Validation reports can become stale if the command is not rerun after artifact changes. | Run `python3 tools/echel.py validate` before release and after validation artifact edits. | TASK-0033 |
| VAL-RISK-002 | Evidence records can become stale if artifacts change after registration. | Re-register evidence after validation artifacts change before running `python3 tools/echel.py readiness --stage release`. | TASK-0036 |
| VAL-RISK-003 | Operations readiness is not yet a dedicated gate. | TASK-0037 added operations artifacts and TASK-0038 added learning capture; add operations readiness checks in a future gate task. | TASK-0039 |
