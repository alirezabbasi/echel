---
type: governance
status: active
stage: governance-integrity
owner: Governance Auditor
---
# Architecture Governance

## Purpose

Architecture governance keeps architecture decisions traceable, boring by default, aligned with domain language, and safe for AI implementation agents.

## Architecture Authority

| Artifact | Authority |
| --- | --- |
| `wiki/architecture/overview.md` | Architectural scope, constraints, guardrails, and accepted major choices. |
| `wiki/architecture/component-architecture.md` | Components, responsibilities, and requirement/domain mappings. |
| `wiki/architecture/data-architecture.md` | Durable data ownership and schema posture. |
| `wiki/architecture/api-architecture.md` | Command, cockpit, and integration contracts. |
| `wiki/architecture/event-architecture.md` | Lifecycle events and graph/update signals. |
| `wiki/architecture/security-architecture.md` | Trust boundaries, command safety, and secret handling. |
| `wiki/architecture/observability-architecture.md` | Visibility into gates, graph, evidence, release, and operations. |
| `wiki/decisions/ADR-*.md` | Accepted architecture decisions and exceptions. |

## Review Rules

| Rule | Required Behavior |
| --- | --- |
| Domain first | Architecture must preserve bounded contexts and domain language from `wiki/domain/`. |
| Requirement traceability | Major components must cite `REQ-###`, `NFR-###`, `BC-###`, or `DM-###` sources. |
| ADR coverage | Material changes to storage, deployment, security, data ownership, agent autonomy, or public interfaces require an ADR. |
| Boring default | Prefer local, simple, inspectable architecture unless a documented constraint justifies complexity. |
| No task-level architecture drift | Implementation tasks must not introduce architecture not present in architecture docs or ADRs. |
| Evidence before release | Architecture-relevant release claims need validation or evidence records. |

## Architecture Change Classes

| Class | Examples | Required Governance |
| --- | --- | --- |
| Minor clarification | Wording, diagram note, cross-reference fix | Update artifact and lifecycle log if downstream references change. |
| Local design change | Component responsibility, internal command contract | Update architecture artifact, graph, affected tests, and task packet. |
| Major decision | Deployment posture, persistent state, trust boundary, data model, public API | Create or update ADR before implementation. |
| Exception | Gate bypass, risk acceptance, non-negotiable trade-off | Record explicit owner decision and mitigation. |

## Architecture Review Checklist

- Architecture references requirement and domain sources.
- Components do not duplicate responsibilities.
- Data, API, security, observability, and operations impacts are addressed.
- ADRs exist for major decisions.
- Work packets cite the accepted architecture source.
- Tests and evidence are planned for architecture-critical behavior.

## Deprecating Architecture

Deprecated architecture must identify the replacement artifact or ADR, affected components, affected tasks, migration path, and rollback note. Deprecated architecture remains visible until migration compatibility passes.
