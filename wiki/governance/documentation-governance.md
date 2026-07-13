---
type: governance
status: active
stage: governance-integrity
owner: Governance Auditor
---
# Documentation Governance

## Purpose

Documentation governance defines how Echel product memory stays coherent as discovery, canon, strategy, requirements, domain, architecture, execution, validation, release, operations, and learning artifacts evolve.

## Source Of Truth Hierarchy

When artifacts disagree, the Governance Auditor resolves or escalates using this order:

| Rank | Source | Authority |
| --- | --- | --- |
| 1 | Accepted ADRs and explicit owner decisions | Final authority for intentional choices and exceptions. |
| 2 | Product Discovery Specification | Verified problem, user, buyer, operator, constraint, risk, and scope facts. |
| 3 | Product Canon | Durable product truth derived from discovery and owner decisions. |
| 4 | Product Strategy | ICP, positioning, wedge, pricing, PMF evidence, and buyer/user model. |
| 5 | Requirements and acceptance criteria | Testable product obligations and boundaries. |
| 6 | Domain model | Business language, bounded contexts, entities, aggregates, events, workflows, and policies. |
| 7 | Architecture and architecture ADRs | System shape, major technical decisions, and trade-offs. |
| 8 | Roadmap, execution phases, and task packets | Delivery sequence and scoped AI-agent work. |
| 9 | Code, tests, evidence, release, operations, and learning records | Implementation proof and operating feedback. |

Lower-ranked artifacts must refine higher-ranked artifacts, not reinterpret them silently. If a lower-ranked artifact reveals an upstream issue, create a contradiction, ADR, risk, or task before changing downstream behavior.

## Duplication Rules

| Rule | Required Behavior |
| --- | --- |
| One canonical home | Each durable concept has one owning artifact. Other artifacts link to it. |
| Summaries are allowed | A downstream artifact may summarize upstream intent only if it links to the source ID or wiki page. |
| Generated sections are bounded | Generated content must stay in clearly marked sections or tables and preserve hand-authored context. |
| Cross-stage copies need trace IDs | Repeated product claims must carry stable methodology IDs or explicit source links. |
| Contradictions are not merged silently | Conflicting claims become contradiction records or accepted ADR exceptions. |

## Deprecation Process

| Step | Action | Owner |
| --- | --- | --- |
| 1 | Mark the stale artifact or section as deprecated with reason, replacement, date, and owner. | Artifact owner |
| 2 | Add a lifecycle log entry and link the replacement artifact. | Governance Auditor |
| 3 | Update downstream references, graph links, task packets, and stage gates. | Affected stage owner |
| 4 | Keep the deprecated artifact available until migration compatibility is verified. | Governance Auditor |
| 5 | Remove or archive only after `make wiki-health` and graph validation pass. | Governance Auditor |

## Required Metadata

Governance-owned artifacts should include:

| Field | Meaning |
| --- | --- |
| `type` | Artifact family, such as `governance`. |
| `status` | `draft`, `active`, `deprecated`, or `superseded`. |
| `stage` | Lifecycle stage that owns the artifact. |
| `owner` | Accountable role. |

## Review Triggers

- A new lifecycle folder or artifact is added.
- An ADR changes architecture, deployment, safety, data, or governance behavior.
- A task changes behavior, tests, evidence, release, operations, or generated project structure.
- A learning record routes follow-up to a task, ADR, risk, assumption, or strategy change.
- A contradiction, stale marker, or low-confidence assumption affects downstream work.

## Acceptance Checks

- Source-of-truth hierarchy is explicit.
- Duplication rules are explicit.
- Deprecation process exists and preserves migration compatibility.
- Downstream docs link to upstream sources instead of copying authority.
- Governance failures create a blocker, accepted exception, contradiction, or remediation task.
