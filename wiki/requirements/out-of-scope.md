---
type: out-of-scope
stage: requirements
status: draft
owner: product
updated: 2026-07-02
---

# Out of Scope

## Purpose

Out-of-scope records protect product focus. They make explicit what will not be built in the current phase, why it is excluded, and what evidence would justify revisiting it.

## Out-of-Scope Register

| ID | Item | Current Phase | Rationale | Source IDs | Related Requirements | Revisit Trigger | Decision Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OOS-001 | Implement `echel requirements` CLI command in TASK-0012 | MVP requirements model | TASK-0012 is scoped to documents and structure; command implementation belongs to TASK-0013 | PLAN-001, TRACE-001 | REQ-005, REQ-006, NFR-005 | Start TASK-0013 | Product/Engineering | Active |
| OOS-002 | Add requirements readiness gate in TASK-0012 | MVP requirements model | Gate implementation depended on command/schema behavior and was completed in TASK-0014 | PLAN-002, TRACE-001 | REQ-005, NFR-005 | Completed TASK-0014 | Product/Engineering | Superseded |
| OOS-003 | Generate downstream tasks directly from requirements | MVP requirements model | Task generation should follow domain, architecture, and planning stages after requirements are stable | CANON-005, STRAT-003 | REQ-001, REQ-004 | Requirements command and gate pass | Product/Engineering | Active |
| OOS-004 | Treat requirement rows as final product truth without review | MVP requirements model | Current rows are structural seed entries and must be refined from real product evidence | PDS-001, CANON-001 | All requirements | Product owner approves evidence-backed requirements | Product | Active |

## Scope Guardrails

- Do not implement automation before the requirement model is stable.
- Do not move unverified later-scope items into MVP without source evidence.
- Do not delete out-of-scope records when priorities change; supersede them with a new decision record.
- Do not use out-of-scope records as substitutes for rejected assumptions or risks.

## Readiness Checklist

- [x] Every out-of-scope item has a reason.
- [x] Every out-of-scope item links to source IDs or planning IDs.
- [x] Every out-of-scope item identifies affected requirements.
- [x] Every out-of-scope item has a revisit trigger.
- [x] MVP exclusions do not conflict with accepted MVP requirements.
