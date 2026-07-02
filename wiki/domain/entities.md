---
type: domain-entities
stage: domain
status: draft
owner: product
updated: 2026-07-02
---

# Entities

## Purpose

Entities are domain concepts with stable identity. They are not storage tables, classes, services, or interface objects.

## Entity Register

| ID | Entity | Identity | Description | Source IDs | Owner Context | Key Relationships | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DM-001 | Product Intent | Intent ID or upstream source ID | Preserved product meaning behind a requirement or downstream artifact. | REQ-001 | BC-001 | Has Source Link; informs Requirement View | Draft |
| DM-002 | Source Link | Source ID | Traceable upstream reference carried by a downstream artifact. | REQ-001, NFR-002 | BC-001 | Links Product Intent to Requirement View | Draft |
| DM-003 | Scope Boundary | Boundary ID | Separation between MVP, later phase, and explicit exclusion. | REQ-002 | BC-002 | Classifies Lifecycle Phase | Draft |
| DM-004 | Lifecycle Phase | Phase name | Delivery horizon used to classify requirements and exclusions. | REQ-002 | BC-002 | Belongs to Scope Boundary | Draft |
| DM-005 | Requirement Dependency | Dependency ID or referenced requirement ID | Known prerequisite that affects planning readiness. | REQ-003 | BC-003 | May create Risk Signal | Draft |
| DM-006 | Risk Signal | Risk ID | Product, validation, or execution concern attached to a requirement. | REQ-003, REQ-004 | BC-003 | Influences Verification Method | Draft |
| DM-007 | Acceptance Criterion | Acceptance ID | Verifiable condition that proves a requirement. | REQ-004, REQ-005 | BC-004 | Has Verification Method | Draft |
| DM-008 | Verification Method | Method ID or method name | Stated way to prove an acceptance criterion. | REQ-004, REQ-005, NFR-003 | BC-004 | Proves Acceptance Criterion | Draft |
| DM-009 | Structured Requirement Field | Field name | Requirement attribute that must be consistently populated. | REQ-005, REQ-006, NFR-005 | BC-001 | Feeds Agent Consumption Contract | Draft |
| DM-010 | Agent Consumption Contract | Contract ID | Minimum product context needed before an AI agent acts. | REQ-006 | BC-005 | Uses Structured Requirement Field | Draft |
| DM-011 | Human-Readable Artifact | Artifact path and title | Product memory artifact readable by domain experts without custom tooling. | NFR-001 | BC-001 | Hosts Requirement View | Draft |
| DM-012 | Stable Identifier | Traceability ID | Identifier whose meaning remains stable after reference. | NFR-002 | BC-001 | Identifies Source Link and Requirement View | Draft |
| DM-013 | Requirement View | View name | A focused document view over requirements, scope, exclusions, NFRs, or acceptance. | NFR-004 | BC-001 | Contains Structured Requirement Fields | Draft |

## Entity Lifecycle Notes

| Entity ID | Created When | Updated When | Retired When |
| --- | --- | --- | --- |
| DM-001 | A requirement receives upstream meaning. | Product intent changes through accepted owner decision. | Superseded by a new source of product truth. |
| DM-003 | A requirement is assigned to a phase or exclusion. | Scope changes through accepted owner decision. | Requirement is superseded or removed. |
| DM-007 | A requirement needs proof. | Acceptance expectations change. | Requirement is superseded or validation no longer applies. |
| DM-010 | Work is prepared for an AI agent. | Required input fields change. | A richer handoff model supersedes it. |

