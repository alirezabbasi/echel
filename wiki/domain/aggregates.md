---
type: domain-aggregates
stage: domain
status: draft
owner: product
updated: 2026-07-02
---

# Aggregates

## Purpose

Aggregates group domain entities that must stay consistent under a business rule. They are not storage, process, or deployment boundaries.

## Aggregate Register

| ID | Aggregate | Root Concept | Included Concepts | Consistency Rule | Source IDs | Owner Context | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AGG-001 | Requirement Memory | DM-001 Product Intent | DM-002 Source Link, DM-009 Structured Requirement Field, DM-012 Stable Identifier, DM-013 Requirement View | A requirement meaning must not change without preserving source links and stable identity. | REQ-001, REQ-005, NFR-002, NFR-004, NFR-005 | BC-001 | Draft |
| AGG-002 | Scope Classification | DM-003 Scope Boundary | DM-004 Lifecycle Phase | A requirement must be classified as MVP, later, or explicitly out of scope before downstream planning. | REQ-002 | BC-002 | Draft |
| AGG-003 | Planning Readiness Record | DM-005 Requirement Dependency | DM-006 Risk Signal | Requirement dependencies and risks must be visible before work is planned. | REQ-003, REQ-004 | BC-003 | Draft |
| AGG-004 | Verification Contract | DM-007 Acceptance Criterion | DM-008 Verification Method | An acceptance criterion is incomplete without a stated verification method. | REQ-004, REQ-005, NFR-003 | BC-004 | Draft |
| AGG-005 | Agent Handoff Context | DM-010 Agent Consumption Contract | DM-009 Structured Requirement Field, DM-003 Scope Boundary, DM-007 Acceptance Criterion | Agent context must include requirement fields, scope, and acceptance before implementation planning. | REQ-006, NFR-005 | BC-005 | Draft |

## Aggregate Invariants

| Aggregate ID | Invariant | Violation Signal | Related Event |
| --- | --- | --- | --- |
| AGG-001 | Stable identifiers and source links remain attached to the same product meaning. | Requirement ID reused for another meaning. | DE-001 Requirement Intent Preserved |
| AGG-002 | MVP and later scope are not mixed silently. | Requirement enters planning without phase. | DE-003 Scope Boundary Changed |
| AGG-003 | Dependencies and risks are populated or explicitly marked as none. | Requirement planned with unknown dependency or risk. | DE-002 Requirement Risk Identified |
| AGG-004 | Acceptance criteria name a verification method. | Requirement has acceptance text but no way to prove it. | DE-004 Acceptance Criterion Linked |
| AGG-005 | Agent handoff uses only gated requirement context. | Agent task is created before requirements, domain, and architecture are ready. | DE-005 Agent Context Prepared |

