---
type: ubiquitous-language
stage: domain
status: draft
owner: product
updated: 2026-07-02
---

# Ubiquitous Language

## Purpose

Ubiquitous language gives every important domain term one definition. Product, domain, architecture, planning, implementation, QA, and operations work should use these terms consistently.

## Authoring Rules

- Use business language first.
- Define one meaning per term.
- Do not use implementation names as domain terms.
- If a term changes meaning, supersede the old row instead of silently editing dependent artifacts.
- Link each term to source requirement IDs.

## Term Register

| ID | Term | Definition | Type | Source IDs | Related Terms | Status |
| --- | --- | --- | --- | --- | --- | --- |
| DM-001 | Product Intent | The product meaning, reason, and owner intent that must survive downstream artifact generation. | Concept | REQ-001 | Source Link, Stable Identifier | Draft |
| DM-002 | Source Link | A traceable connection from an artifact to upstream discovery, canon, strategy, requirement, or decision IDs. | Concept | REQ-001, NFR-002 | Product Intent, Stable Identifier | Draft |
| DM-003 | Scope Boundary | The explicit separation between what belongs in MVP, what belongs later, and what is excluded. | Concept | REQ-002 | Lifecycle Phase, Requirement View | Draft |
| DM-004 | Lifecycle Phase | A named product delivery horizon used to classify scope. | Concept | REQ-002 | Scope Boundary | Draft |
| DM-005 | Requirement Dependency | A prerequisite that must be known before a requirement can be planned or executed. | Concept | REQ-003 | Risk Signal | Draft |
| DM-006 | Risk Signal | A visible concern that may affect product validity, planning quality, validation, or execution. | Concept | REQ-003, REQ-004 | Requirement Dependency | Draft |
| DM-007 | Acceptance Criterion | A verifiable condition that proves one or more requirements are satisfied. | Concept | REQ-004, REQ-005 | Verification Method | Draft |
| DM-008 | Verification Method | The review, test, inspection, or evidence method used to prove acceptance. | Concept | REQ-004, REQ-005, NFR-003 | Acceptance Criterion | Draft |
| DM-009 | Structured Requirement Field | A named requirement attribute such as priority, phase, dependency, risk, acceptance, or source ID. | Concept | REQ-005, REQ-006, NFR-005 | Requirement View | Draft |
| DM-010 | Agent Consumption Contract | The structured context an AI agent must receive before it can safely act on product work. | Concept | REQ-006 | Structured Requirement Field | Draft |
| DM-011 | Human-Readable Artifact | A product memory artifact that a domain expert can inspect without custom tooling. | Concept | NFR-001 | Requirement View | Draft |
| DM-012 | Stable Identifier | A traceability ID whose meaning does not change after downstream artifacts reference it. | Concept | NFR-002 | Source Link | Draft |
| DM-013 | Requirement View | A focused requirements document that presents one concern clearly, such as MVP scope or acceptance criteria. | Concept | NFR-004 | Structured Requirement Field | Draft |

## Synonyms And Forbidden Meanings

| Term | Accepted Synonyms | Forbidden Meanings | Reason |
| --- | --- | --- | --- |
| Product Intent | Product meaning, owner intent | Marketing slogan, vague vision | Intent must stay traceable and actionable. |
| Source Link | Trace link, upstream reference | File path only | A source link must identify product meaning, not only location. |
| Scope Boundary | Scope line, phase boundary | Backlog bucket | Scope boundaries govern lifecycle progression. |
| Acceptance Criterion | Acceptance condition | Task checklist only | Criteria prove requirements, not only task completion. |
| Verification Method | Validation method, review method | Implementation detail | Verification states how truth is proven. |

## Open Language Questions

| ID | Question | Affected Terms | Owner | Status |
| --- | --- | --- | --- | --- |
| Q-DM-001 | Should generated requirement rows and hand-authored requirement rows share the same domain term set? | Structured Requirement Field, Requirement View | Product | Open |

