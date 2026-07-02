---
type: domain-overview
stage: domain
status: draft
owner: product
updated: 2026-07-02
---

# Domain Overview

## Purpose

The domain model turns gated requirements into stable product language before architecture begins. It defines the business concepts, boundaries, workflows, events, and rules that architecture must preserve.

This document is intentionally technology-neutral. It may mention a technology only when the item is explicitly marked as a constraint inherited from discovery, canon, strategy, or requirements.

## Source Inputs

- Requirements: [[../requirements/product-requirements]], [[../requirements/functional-requirements]], [[../requirements/non-functional-requirements]]
- MVP scope: [[../requirements/mvp-scope]]
- Acceptance criteria: [[../requirements/acceptance-criteria]]
- Product canon: [[../canon/product-canon]], [[../canon/non-negotiables]]
- Traceability contract: `schema/traceability.schema.md`

## Domain Modeling Rules

- Use `DM-###` for domain concepts and entities.
- Use `BC-###` for bounded contexts.
- Use `DE-###` for domain events.
- Use `BR-###` for business rules and policies.
- Every requirement must map to at least one `DM-###`, `BC-###`, `DE-###`, or `BR-###`.
- Each important term must have one definition in [[ubiquitous-language]].
- Business rules must describe business truth, not storage, framework, integration, or deployment design.
- Architecture decisions begin only after the domain model is stable.

## Domain Scope

| ID | Name | Type | Definition | Source Requirements | Owner Context | Status |
| --- | --- | --- | --- | --- | --- | --- |
| DM-001 | Product Intent | Concept | The preserved reason and product meaning behind a downstream artifact. | REQ-001 | BC-001 | Draft |
| DM-002 | Source Link | Concept | A traceable reference from a downstream artifact to an upstream source ID. | REQ-001, NFR-002 | BC-001 | Draft |
| DM-003 | Scope Boundary | Concept | The explicit line between MVP, later scope, and excluded scope. | REQ-002 | BC-002 | Draft |
| DM-004 | Lifecycle Phase | Concept | A named delivery horizon such as MVP, V1, V2, or Future. | REQ-002 | BC-002 | Draft |
| DM-005 | Requirement Dependency | Concept | A known prerequisite that affects planning or readiness. | REQ-003 | BC-003 | Draft |
| DM-006 | Risk Signal | Concept | A visible product, validation, or execution concern tied to an artifact. | REQ-003, REQ-004 | BC-003 | Draft |
| DM-007 | Acceptance Criterion | Concept | A verifiable condition that proves a requirement is satisfied. | REQ-004, REQ-005 | BC-004 | Draft |
| DM-008 | Verification Method | Concept | The review or test approach used to prove acceptance. | REQ-004, REQ-005, NFR-003 | BC-004 | Draft |
| DM-009 | Structured Requirement Field | Concept | A predictable requirement attribute used by humans and future automation. | REQ-005, REQ-006, NFR-005 | BC-001 | Draft |
| DM-010 | Agent Consumption Contract | Concept | The minimum structured context an AI agent needs before acting. | REQ-006 | BC-005 | Draft |
| DM-011 | Human-Readable Artifact | Concept | A product memory artifact that remains understandable without custom tooling. | NFR-001 | BC-001 | Draft |
| DM-012 | Stable Identifier | Concept | A traceability ID that is not reused for a different meaning. | NFR-002 | BC-001 | Draft |
| DM-013 | Requirement View | Concept | A dedicated requirement document view for a specific concern. | NFR-004 | BC-001 | Draft |

## Requirement To Domain Coverage

| Requirement ID | Domain Concepts | Bounded Contexts | Rules or Events | Coverage Status |
| --- | --- | --- | --- | --- |
| REQ-001 | DM-001, DM-002, DM-012 | BC-001 | BR-001 | Covered |
| REQ-002 | DM-003, DM-004 | BC-002 | BR-002 | Covered |
| REQ-003 | DM-005, DM-006 | BC-003 | BR-003 | Covered |
| REQ-004 | DM-006, DM-007, DM-008 | BC-004 | BR-004 | Covered |
| REQ-005 | DM-007, DM-008, DM-009 | BC-001, BC-004 | BR-005 | Covered |
| REQ-006 | DM-009, DM-010 | BC-005 | BR-006 | Covered |
| NFR-001 | DM-011, DM-013 | BC-001 | BR-007 | Covered |
| NFR-002 | DM-002, DM-012 | BC-001 | BR-001 | Covered |
| NFR-003 | DM-007, DM-008 | BC-004 | BR-004 | Covered |
| NFR-004 | DM-013 | BC-001 | BR-008 | Covered |
| NFR-005 | DM-009, DM-010 | BC-001, BC-005 | BR-006 | Covered |

## Technology Constraint Register

| Constraint ID | Statement | Source IDs | Applies To | Notes |
| --- | --- | --- | --- | --- |
| TBD | No technology constraint declared in the domain model. | TBD | TBD | Add a row only when an upstream constraint requires it. |

## Domain Handoff To Architecture

Architecture may start only after:

- requirement coverage is complete;
- domain terms have one definition;
- bounded contexts identify responsibilities and forbidden responsibilities;
- workflows, policies, and events are documented;
- technology choices are absent or explicitly marked as constraints.

