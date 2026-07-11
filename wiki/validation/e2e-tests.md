---
type: validation
status: draft
stage: validation
---
# E2E Tests

## Purpose

End-to-end tests prove that a product owner and AI-agent team can move through the Echel lifecycle without losing source intent, bypassing gates, or inventing implementation scope.

## E2E Workflow Matrix

| Test ID | Workflow | Requirement IDs | Task IDs | Domain IDs | Acceptance Criteria | Expected Proof | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TEST-E2E-001 | Discovery to canon to strategy to requirements. | REQ-001, NFR-002 | TASK-0004..TASK-0014 | DM-012, BC-001 | AC-001, AC-007 | Source IDs remain visible from PDS/canon/strategy into requirement rows. | Planned |
| TEST-E2E-002 | Requirements to domain to architecture to roadmap. | REQ-003, REQ-005 | TASK-0015..TASK-0022 | DM-201, BC-201, ARCH-204 | AC-004, AC-005 | Domain and architecture mappings cover MVP requirements before roadmap execution. | Planned |
| TEST-E2E-003 | Roadmap to execution tasks to repository factory. | REQ-004, REQ-006, NFR-001 | TASK-0023, TASK-0024, TASK-0025 | DM-005, BC-003 | AC-003, AC-006 | Generated task packets and repository baseline expose exact verification commands. | Planned |
| TEST-E2E-004 | Agent role handoff to implementation-safe task execution. | REQ-004, REQ-006 | TASK-0026, TASK-0027, TASK-0028 | DM-005, BC-003 | AC-003, AC-006 | Playbooks require handoff summary and no code before approved task packet. | Planned |
| TEST-E2E-005 | Validation report to evidence-backed release readiness. | REQ-004, NFR-003 | TASK-0032, TASK-0033, TASK-0034, TASK-0036 | DM-006, BC-003 | AC-003 | Validation report lists pass/fail/skipped/blockers and evidence links. | Planned |

## E2E Acceptance Rules

- A workflow fails if any required stage gate is bypassed without an explicit force/exception record.
- A workflow is blocked if required evidence cannot be registered.
- A workflow is skipped only when its downstream task has not been implemented yet.
