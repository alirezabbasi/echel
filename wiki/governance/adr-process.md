---
type: governance
status: active
stage: governance-integrity
owner: Governance Auditor
---
# ADR Process

## Purpose

The ADR process records major decisions so AI agents can understand what is settled, what is rejected, and what must not be changed silently.

## When An ADR Is Required

Create or update an ADR when a change affects:

| Trigger | Examples |
| --- | --- |
| Architecture shape | Components, bounded contexts, data ownership, command boundaries, generated repository structure. |
| Trust or safety | Secret handling, command exposure, agent autonomy, write boundaries, evidence rules. |
| Release posture | Deployment path, rollback model, production checklist, readiness gate behavior. |
| Source-of-truth policy | Folder ownership, migration compatibility, generated vs hand-authored authority. |
| Accepted exception | Gate bypass, unresolved risk acceptance, significant technical debt. |

## ADR Lifecycle

| Status | Meaning |
| --- | --- |
| Proposed | Decision is under review and cannot guide implementation yet. |
| Accepted | Decision is authoritative until superseded. |
| Superseded | Decision has a replacement ADR or governance artifact. |
| Rejected | Option was considered and intentionally not chosen. |

## Required ADR Sections

- Context.
- Decision.
- Consequences.
- Alternatives considered.
- Source IDs and affected artifacts.
- Verification or evidence expectations.
- Supersession note when replacing a prior ADR.

## Numbering

ADRs use `ADR-####` IDs and live in `wiki/decisions/`. The filename should include the ID and a stable slug.

## Cross-Reference Requirements

Every accepted ADR should be linked from affected architecture docs, task packets, release or operations docs when relevant, and product graph nodes when graph extraction supports the artifact family.

## Deprecation And Supersession

An ADR is never deleted to hide history. Superseded ADRs must link to the replacement ADR and explain whether downstream artifacts must change.
