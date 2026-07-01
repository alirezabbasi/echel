---
type: discovery-assumptions
status: draft
stage: discovery
---
# Assumptions

This document tracks all assumptions, hypotheses, and open questions for the product. Every entry must include a traceability ID, statement type, confidence level, and validation method.

## Active Assumptions

| ID | Assumption | Confidence | Impact if Wrong | Validation Method | Status | Resolved By |
| --- | --- | --- | --- | --- | --- | --- |
| `A-001` | TBD | TBD | TBD | TBD | active | TBD |

## Active Hypotheses

| ID | Hypothesis | Confidence | Test Method | Success Signal | Failure Signal | Status | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `H-001` | TBD | TBD | TBD | TBD | TBD | active | TBD |

## Open Questions

| ID | Question | Owner | Priority | Due Date | Status | Answer |
| --- | --- | --- | --- | --- | --- | --- |
| `Q-001` | TBD | TBD | TBD | TBD | open | TBD |

## Resolved Items

| ID | Original Type | Statement | Resolution | Resolved Date | Changed Downstream |
| --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD |

## Assumption Tracking Rules

- Every assumption must be validated or explicitly accepted before the discovery gate passes.
- Low-confidence assumptions that affect scope, architecture, or release readiness must remain visible until resolved.
- When an assumption is validated, update its status to `validated` and record the evidence.
- When an assumption is invalidated, record the contradiction and propagate the change to all downstream artifacts that referenced it.
- Hypotheses must be tested with explicit success and failure signals before they can be promoted to facts.
- Open questions must have an owner and a due date.

## Confidence Validation Rules

| Confidence | Required Action |
| --- | --- |
| high | Evidence must exist or owner must explicitly accept responsibility. |
| medium | Validation plan must exist within current lifecycle stage. |
| low | Must not block downstream stages. Must be escalated or resolved before release. |
