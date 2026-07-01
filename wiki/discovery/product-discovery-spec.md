---
type: product-discovery-spec
status: draft
stage: discovery
---
# Product Discovery Specification

This document is the founder/platform contract. It captures everything the platform needs to know before any downstream work begins. Every statement must be classified by type and confidence. Important entries must carry a traceability ID.

## Statement Types

Every statement in this document must be tagged with one of:

| Type | Meaning |
| --- | --- |
| fact | Verified information |
| observation | Directly observed |
| assumption | Believed but unverified |
| hypothesis | Needs testing |
| decision | Explicitly chosen |
| constraint | Cannot be changed |
| risk | Possible negative outcome |
| question | Still unresolved |

## Confidence Levels

Important entries must include a confidence level:

- `high`: strong evidence or owner certainty.
- `medium`: plausible but needs validation.
- `low`: weakly supported or exploratory.

AI agents must never treat assumptions or hypotheses as facts.

---

## 01 Executive Summary

| Field | Value |
| --- | --- |
| Product Name | TBD |
| One-sentence description | TBD |
| Category | TBD |
| Target industry | TBD |
| Current stage | Discovery |
| Author | TBD |
| Date | TBD |
| Revision | TBD |

---

## 02 Problem

**Statement type:** fact or observation
**Confidence:** TBD

### Problem Statement {#P-001}

- ID: `P-001`
- Type: TBD
- Confidence: TBD

TBD

### Current Process

TBD

### Current Pain

TBD

### Why Existing Solutions Fail

TBD

### Cost of Doing Nothing

TBD

### Evidence

TBD

### Urgency

TBD

### Who Experiences It

TBD

### Frequency

TBD

### Severity

TBD

---

## 03 Users

### Primary Users {#U-001}

| ID | Role | Description | Statement Type | Confidence |
| --- | --- | --- | --- | --- |
| `U-001` | TBD | TBD | TBD | TBD |

### User Goals

TBD

### User Constraints

TBD

---

## 04 Buyers

### Buyer Model {#B-001}

| ID | Role | Description | Statement Type | Confidence |
| --- | --- | --- | --- | --- |
| `B-001` | TBD | TBD | TBD | TBD |

### Economic Buyer

- Who signs the contract? TBD
- Who pays? TBD
- Who approves? TBD
- Who blocks? TBD
- Who influences? TBD

---

## 05 Operators

### Operator Model {#O-001}

| ID | Role | Description | Statement Type | Confidence |
| --- | --- | --- | --- | --- |
| `O-001` | TBD | TBD | TBD | TBD |

---

## 06 Current Workflow

### Workflow {#WF-001}

- ID: `WF-001`
- Type: TBD
- Confidence: TBD

Describe the current process step by step without the proposed product.

TBD

### Workflow Steps

1. TBD
2. TBD
3. TBD

---

## 07 Pain Points

### Pain Point {#PP-001}

| ID | Description | Frequency | Business Cost | Operational Cost | Workaround | Root Cause | Importance | Statement Type | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `PP-001` | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

---

## 08 Proposed Solution

**Statement type:** decision or hypothesis
**Confidence:** TBD

### Solution Concept

TBD

### Core Capabilities

- TBD

### Differentiation

TBD

---

## 09 Product Vision

**Statement type:** decision
**Confidence:** TBD

Where does this product end? What business transformation happens?

TBD

---

## 10 Business Model

**Statement type:** assumption or hypothesis
**Confidence:** TBD

How does money flow?

- License: TBD
- SaaS: TBD
- Subscription: TBD
- Marketplace: TBD
- Professional Services: TBD
- Support: TBD
- Training: TBD
- Usage: TBD
- Revenue Share: TBD

---

## 11 Success Criteria

### Business Success {#S-001}

| ID | Criterion | Type | Confidence |
| --- | --- | --- | --- |
| `S-001` | TBD | TBD | TBD |

### Technical Success

| ID | Criterion | Type | Confidence |
| --- | --- | --- | --- |
| `S-002` | TBD | TBD | TBD |

### Operational Success

| ID | Criterion | Type | Confidence |
| --- | --- | --- | --- |
| `S-003` | TBD | TBD | TBD |

### Customer Success

| ID | Criterion | Type | Confidence |
| --- | --- | --- | --- |
| `S-004` | TBD | TBD | TBD |

### Financial Success

| ID | Criterion | Type | Confidence |
| --- | --- | --- | --- |
| `S-005` | TBD | TBD | TBD |

---

## 12 Scope

### MVP

- TBD

### Version 1

- TBD

### Version 2

- TBD

### Future

- TBD

---

## 13 Non-Goals

**Statement type:** decision

| ID | Non-Goal | Rationale |
| --- | --- | --- |
| `NC-001` | TBD | TBD |

Without explicit non-goals, scope expands forever.

---

## 14 Constraints

| ID | Constraint | Category | Statement Type | Confidence |
| --- | --- | --- | --- | --- |
| `C-001` | TBD | budget | TBD | TBD |
| `C-002` | TBD | time | TBD | TBD |
| `C-003` | TBD | people | TBD | TBD |
| `C-004` | TBD | technology | TBD | TBD |
| `C-005` | TBD | legal | TBD | TBD |
| `C-006` | TBD | compliance | TBD | TBD |

---

## 15 Assumptions

**Statement type:** assumption

| ID | Assumption | Confidence | Impact if Wrong | Validation Method |
| --- | --- | --- | --- | --- |
| `A-001` | TBD | TBD | TBD | TBD |

---

## 16 Hypotheses

**Statement type:** hypothesis

| ID | Hypothesis | Confidence | Test Method | Success Signal | Failure Signal |
| --- | --- | --- | --- | --- | --- |
| `H-001` | TBD | TBD | TBD | TBD | TBD |

---

## 17 Risks

| ID | Risk | Category | Impact | Likelihood | Mitigation | Statement Type | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `R-001` | TBD | business | TBD | TBD | TBD | TBD | TBD |
| `R-002` | TBD | technical | TBD | TBD | TBD | TBD | TBD |
| `R-003` | TBD | operational | TBD | TBD | TBD | TBD | TBD |
| `R-004` | TBD | financial | TBD | TBD | TBD | TBD | TBD |
| `R-005` | TBD | market | TBD | TBD | TBD | TBD | TBD |
| `R-006` | TBD | execution | TBD | TBD | TBD | TBD | TBD |
| `R-007` | TBD | legal | TBD | TBD | TBD | TBD | TBD |
| `R-008` | TBD | vendor | TBD | TBD | TBD | TBD | TBD |

---

## 18 Competitive Landscape

| ID | Alternative | Type | Strength | Weakness | Switching Cost |
| --- | --- | --- | --- | --- | --- |
| `CMP-001` | TBD | TBD | TBD | TBD | TBD |

Current alternatives include not only software but also Excel, email, phone, consultants, legacy systems, custom software, and doing nothing.

---

## 19 Functional Overview

High level capabilities. No architecture.

- TBD

---

## 20 Non-Functional Expectations

| Category | Expectation | Statement Type | Confidence |
| --- | --- | --- | --- |
| Availability | TBD | TBD | TBD |
| Performance | TBD | TBD | TBD |
| Scalability | TBD | TBD | TBD |
| Security | TBD | TBD | TBD |
| Compliance | TBD | TBD | TBD |
| Observability | TBD | TBD | TBD |
| Maintainability | TBD | TBD | TBD |

---

## 21 Business Rules

| ID | Rule | Statement Type | Confidence |
| --- | --- | --- | --- |
| `BR-001` | TBD | TBD | TBD |

Business rules are business truth, not database design.

---

## 22 Open Questions

| ID | Question | Owner | Priority | Due Date | Statement Type |
| --- | --- | --- | --- | --- | --- |
| `Q-001` | TBD | TBD | TBD | TBD | question |

Do not hide unknowns.

---

## 23 Research Plan

| ID | Topic | Method | Owner | Due Date | Status |
| --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | not started |

Research areas:
- Market
- Technology
- Legal
- Domain
- Competition

---

## 24 References

- Papers: TBD
- Products: TBD
- Links: TBD
- Standards: TBD
- Specifications: TBD

---

## 25 Appendix

Sketches, whiteboard notes, screenshots, raw ideas.

TBD

---

## Quality Gate

Before proceeding to Product Canon, this document must pass:

- [ ] Problem clearly defined
- [ ] Buyer identified
- [ ] User identified
- [ ] Operator identified
- [ ] Current workflow documented
- [ ] Business value measurable
- [ ] Non-goals documented
- [ ] Constraints documented
- [ ] Success criteria measurable
- [ ] Major risks identified
- [ ] Assumptions listed with confidence
- [ ] Open questions documented
- [ ] Research plan exists
- [ ] MVP scope defined

If one fails, do not proceed.

---

## Traceability

This document originates the following ID families:

- `P-###`: problem and pain points
- `U-###`: users
- `B-###`: buyers
- `O-###`: operators
- `WF-###`: workflows
- `PP-###`: pain points
- `A-###`: assumptions
- `H-###`: hypotheses
- `R-###`: risks
- `S-###`: success criteria
- `Q-###`: open questions
- `C-###`: constraints
- `NC-###`: non-goals
- `BR-###`: business rules

Downstream artifacts must reference these IDs rather than reinterpreting the content.
