---
type: contradiction-register
status: active
stage: governance-integrity
owner: Governance Auditor
---
# Contradiction Register

## Purpose

This artifact promotes contradiction records from local runtime memory into committed product memory so conflicting claims are visible, traceable, and resolvable by future agents.

## Resolution Workflow

1. Capture the conflicting claim as a contradiction memory record or refresh this register with `python3 tools/echel.py contradictions sync`.
2. Link both sides of the conflict through source IDs, files, ADRs, requirements, risks, or task IDs.
3. Assign the generated resolution task to the accountable lifecycle role.
4. Resolve by updating the upstream source of truth, creating an ADR, accepting an exception, or opening a scoped execution task.
5. Mark the contradiction `Resolved` only after downstream artifacts and graph traceability are synchronized.

## Register

| ID | Status | Title | Source Record | Type | Links | Impact | Resolution Task | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONTR-000 | Resolved | No product-memory contradictions recorded | `none` | none | None | No current contradiction impact. | CONTR-TASK-000 | Governance Auditor |

## Resolution Tasks

| Task ID | Contradiction | Required Action | Verification | Status |
| --- | --- | --- | --- | --- |
| CONTR-TASK-000 | CONTR-000 | No action required. | Re-run sync after new contradiction records are captured. | Resolved |

## Graph Contract

- Each register row becomes a `contradiction` node in `wiki/graph.json`.
- Open contradiction rows remain governance-stage observations until resolved.
- Resolution tasks keep contradictions actionable without hiding them in local memory.
