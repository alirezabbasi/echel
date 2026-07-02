---
type: domain-events
stage: domain
status: draft
owner: product
updated: 2026-07-02
---

# Domain Events

## Purpose

Domain events record meaningful business-domain changes. They are not implementation messages, integration events, queues, or notifications.

## Event Register

| ID | Event | Meaning | Trigger | Source IDs | Publisher Context | Consumer Contexts | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DE-001 | Requirement Intent Preserved | A requirement keeps upstream product intent and source links. | Requirement row includes stable source IDs. | REQ-001, NFR-002 | BC-001 | BC-002, BC-003, BC-004, BC-005 | Draft |
| DE-002 | Requirement Risk Identified | A requirement receives a visible risk or dependency concern. | Dependency or risk field is populated or changed. | REQ-003, REQ-004 | BC-003 | BC-004, BC-005 | Draft |
| DE-003 | Scope Boundary Changed | A requirement changes MVP, later, or excluded classification. | Phase, MVP scope, or out-of-scope record changes. | REQ-002 | BC-002 | BC-001, BC-005 | Draft |
| DE-004 | Acceptance Criterion Linked | A requirement is linked to an acceptance criterion and verification method. | Acceptance field references an `AC-###` row. | REQ-004, REQ-005, NFR-003 | BC-004 | BC-005 | Draft |
| DE-005 | Agent Context Prepared | Requirement context is ready for future agent-facing work. | Required structured fields are available for handoff. | REQ-006, NFR-005 | BC-005 | Future execution planning | Draft |

## Event Rules

| Event ID | Must Include | Must Not Include |
| --- | --- | --- |
| DE-001 | Requirement ID, source IDs, affected domain concepts. | Storage or implementation details. |
| DE-002 | Requirement ID, risk or dependency statement, owner decision if accepted. | Hidden assumptions. |
| DE-003 | Requirement ID, old phase, new phase, reason. | Silent scope changes. |
| DE-004 | Requirement ID, acceptance ID, verification method. | Untestable acceptance text. |
| DE-005 | Requirement ID, domain concept IDs, acceptance IDs, current phase. | Implementation instructions before architecture. |

