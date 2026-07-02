---
type: bounded-contexts
stage: domain
status: draft
owner: product
updated: 2026-07-02
---

# Bounded Contexts

## Purpose

Bounded contexts define ownership boundaries in the product domain. They describe responsibilities, forbidden responsibilities, owned terms, workflows, policies, and events without choosing implementation structure.

## Context Register

| ID | Context | Responsibility | Owned Concepts | Source IDs | Status |
| --- | --- | --- | --- | --- | --- |
| BC-001 | Product Memory Governance | Preserve traceable product memory and stable requirement fields. | DM-001, DM-002, DM-009, DM-011, DM-012, DM-013 | REQ-001, REQ-005, NFR-001, NFR-002, NFR-004, NFR-005 | Draft |
| BC-002 | Scope Control | Keep MVP, later scope, and exclusions separated. | DM-003, DM-004 | REQ-002 | Draft |
| BC-003 | Planning Readiness | Expose requirement dependencies and risks before downstream planning. | DM-005, DM-006 | REQ-003, REQ-004 | Draft |
| BC-004 | Validation Contract | Define acceptance criteria and verification methods for requirements. | DM-007, DM-008 | REQ-004, REQ-005, NFR-003 | Draft |
| BC-005 | Agent Handoff | Shape requirement context for future AI-agent consumption. | DM-010, DM-009 | REQ-006, NFR-005 | Draft |

## Context Details

| Context ID | Commands Or Decisions | Queries Or Reviews | Events Published | Events Consumed | Forbidden Responsibilities |
| --- | --- | --- | --- | --- | --- |
| BC-001 | Assign stable IDs; preserve source links; maintain requirement views. | Which requirements lack traceable source? Which fields changed? | DE-001 Requirement Intent Preserved | DE-003 Scope Boundary Changed | Does not decide delivery scope or architecture. |
| BC-002 | Classify MVP, later, and excluded scope. | Which requirements are MVP? Which exclusions apply? | DE-003 Scope Boundary Changed | DE-001 Requirement Intent Preserved | Does not define acceptance evidence. |
| BC-003 | Record dependencies and risk signals. | Which requirements are blocked? Which risks affect planning? | DE-002 Requirement Risk Identified | DE-001 Requirement Intent Preserved | Does not resolve risks without owner decision. |
| BC-004 | Link acceptance criteria and verification methods. | Which requirements are testable? Which criteria lack evidence? | DE-004 Acceptance Criterion Linked | DE-002 Requirement Risk Identified | Does not implement tests or architecture. |
| BC-005 | Prepare agent-readable context from approved requirement fields. | Which fields are required for agent handoff? | DE-005 Agent Context Prepared | DE-004 Acceptance Criterion Linked | Does not create implementation tasks before domain and architecture are ready. |

## Context Relationship Map

| From Context | Relationship | To Context | Reason |
| --- | --- | --- | --- |
| BC-001 | supplies source memory to | BC-002 | Scope decisions need stable requirement identity. |
| BC-001 | supplies source memory to | BC-003 | Dependency and risk records need stable requirement identity. |
| BC-003 | informs | BC-004 | Risks and dependencies affect verification. |
| BC-004 | prepares evidence expectations for | BC-005 | Agent handoff needs testable context. |
| BC-002 | constrains | BC-005 | Agents must not receive later-scope work as MVP work. |

