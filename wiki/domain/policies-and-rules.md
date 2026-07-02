---
type: domain-policies-and-rules
stage: domain
status: draft
owner: product
updated: 2026-07-02
---

# Policies And Rules

## Purpose

Policies and rules define business truth for the domain model. They constrain later architecture and execution without selecting technical mechanisms.

## Business Rule Register

| ID | Rule | Source IDs | Applies To | Enforcement Moment | Status |
| --- | --- | --- | --- | --- | --- |
| BR-001 | A requirement must preserve upstream source IDs when it is used by downstream artifacts. | REQ-001, NFR-002 | DM-001, DM-002, DM-012 | Requirement review and domain handoff | Draft |
| BR-002 | A requirement must be classified as MVP, later, or explicitly out of scope before downstream planning. | REQ-002 | DM-003, DM-004 | Scope boundary review | Draft |
| BR-003 | A requirement dependency must be known or explicitly marked as none before planning. | REQ-003 | DM-005 | Planning readiness review | Draft |
| BR-004 | A requirement risk must remain visible until accepted, mitigated, or superseded. | REQ-004 | DM-006 | Planning and validation review | Draft |
| BR-005 | An acceptance criterion must identify a verification method before implementation planning. | REQ-004, REQ-005, NFR-003 | DM-007, DM-008 | Acceptance readiness review | Draft |
| BR-006 | Agent-facing work must be generated from structured requirement fields and covered domain concepts. | REQ-006, NFR-005 | DM-009, DM-010 | Agent handoff preparation | Draft |
| BR-007 | Domain and requirement artifacts must remain readable by a domain expert without custom tooling. | NFR-001 | DM-011, DM-013 | Documentation review | Draft |
| BR-008 | Requirement views must keep distinct concerns separate instead of merging scope, NFRs, and acceptance into one ambiguous document. | NFR-004 | DM-013 | Requirement model review | Draft |

## Policy Register

| ID | Policy | Reason | Source IDs | Status |
| --- | --- | --- | --- | --- |
| POL-DM-001 | Do not introduce architecture or implementation choices in domain artifacts unless marked as upstream constraints. | Domain language must stay stable before architecture. | schema/lifecycle-stage.schema.md, TASK-0015 | Active |
| POL-DM-002 | Supersede changed domain terms instead of silently reusing an ID for a new meaning. | Stable traceability protects downstream work. | NFR-002, TRACE-001 | Active |
| POL-DM-003 | Every future generated domain row must preserve requirement IDs in `Source IDs`. | Domain automation must preserve requirement intent. | REQ-001, REQ-006 | Active |

## Rule Coverage

| Requirement ID | Rules |
| --- | --- |
| REQ-001 | BR-001 |
| REQ-002 | BR-002 |
| REQ-003 | BR-003 |
| REQ-004 | BR-004, BR-005 |
| REQ-005 | BR-005 |
| REQ-006 | BR-006 |
| NFR-001 | BR-007 |
| NFR-002 | BR-001, POL-DM-002 |
| NFR-003 | BR-005 |
| NFR-004 | BR-008 |
| NFR-005 | BR-006, POL-DM-003 |

