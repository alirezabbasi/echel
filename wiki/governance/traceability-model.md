---
type: governance
status: active
stage: governance-integrity
owner: Governance Auditor
---
# Traceability Model

## Purpose

The traceability model defines how Echel proves that product intent survives from discovery through implementation, validation, release, operations, and learning.

## Canonical Chain

```text
discovery item
-> canon statement
-> strategy choice
-> requirement
-> domain concept or bounded context
-> architecture decision or component
-> roadmap phase
-> task packet
-> test
-> evidence
-> release or operations record
```

## Required Link Types

| From | To | Required Evidence |
| --- | --- | --- |
| Discovery | Canon | Discovery ID or source section link. |
| Canon | Strategy | Canon section or statement ID. |
| Strategy | Requirement | Strategy ID or artifact link. |
| Requirement | Domain | `REQ-###` mapped to `DM-###`, `BC-###`, `AGG-###`, `DE-###`, or business rule. |
| Domain | Architecture | Domain IDs in architecture tables. |
| Architecture | Task | Architecture item or ADR cited by task packet. |
| Task | Test | Test ID or validation row. |
| Test | Evidence | `EVID-###` registry record or planned evidence target. |
| Evidence | Release | Proof pack, release summary, or production checklist row. |
| Operations | Backlog or Decision | Learning record routed to task, ADR, risk, assumption, or strategy change. |

## Traceability Reports

| Report | Purpose |
| --- | --- |
| `wiki/reports/traceability-matrix.md` | Shows lifecycle coverage and broken chains. |
| `wiki/reports/product-graph-report.md` | Shows graph node coverage and validation issues. |
| `wiki/reports/wiki-health-report.md` | Shows wiki integrity and link health. |

## Broken Chain Handling

Broken chains are classified as:

| Class | Response |
| --- | --- |
| Missing source | Add source ID or link to upstream artifact. |
| Missing downstream artifact | Create follow-up task or mark scope intentionally deferred. |
| Stale link | Update link and record the change in lifecycle log. |
| Contradiction | Create contradiction artifact or ADR exception. |
| Evidence gap | Register evidence or keep release blocked. |

## Minimum Governance Standard

MVP-relevant requirements must trace to domain, architecture, task, validation, and evidence. If evidence does not exist yet, the traceability matrix must show the gap explicitly.
