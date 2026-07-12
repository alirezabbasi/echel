---
type: operations-change-management
stage: operations
status: draft
owner: operations-steward
updated: 2026-07-13
---
# Change Management

## Purpose

This document governs post-release changes so improvements, fixes, and operational adjustments preserve traceability, evidence, and product memory.

## Source Inputs

- Execution tasks: [[../work/TASK_INDEX]]
- Release process: [[../deployment/release-process]]
- Evidence registry: `.echel/evidence_registry.json`
- Decision log: [[../../docs/development/state/decision-log]]
- Evolution backlog: [[evolution-backlog]]

## Change Classes

| ID | Change Class | Examples | Required Review | Required Evidence | Approval Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| CHG-001 | Standard change | Documentation update, generated artifact refresh, non-behavioral cleanup | Documentation review | Updated wiki artifact and validation command output | Operations Steward | Draft |
| CHG-002 | Product behavior change | Requirement, workflow, domain, or architecture behavior change | Product Manager and Solution Architect review | Task packet, tests, evidence record | Product Manager | Draft |
| CHG-003 | Release change | Deployment, rollback, production checklist, or environment change | Release Manager review | Release gate output and evidence record | Release Manager | Draft |
| CHG-004 | Emergency change | Incident mitigation or security response | Post-change governance review | Incident record, rollback/mitigation evidence, RCA follow-up | Governance Auditor | Draft |

## Change Workflow

| ID | Step | Action | Required Artifact | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| CHG-WF-001 | Intake | Capture source, reason, affected lifecycle artifacts, and proposed class. | Evolution backlog or task packet | Operations Steward | Draft |
| CHG-WF-002 | Impact analysis | Identify affected requirements, domain, architecture, tests, deployment, and evidence. | Traceability matrix or graph report | Governance Auditor | Draft |
| CHG-WF-003 | Approval | Confirm owner approval and required gate expectations. | Decision note or task packet | Change owner | Draft |
| CHG-WF-004 | Implementation | Execute through an approved task packet when code or product behavior changes. | `wiki/work/TASK-*.md` | Implementation Agent | Draft |
| CHG-WF-005 | Verification | Run tests, validation, release gate, or wiki-health command required by the change class. | Evidence registry entry | QA Agent | Draft |
| CHG-WF-006 | Memory update | Update changed artifacts, decisions, risks, operations docs, and backlog status. | Updated wiki memory | Operations Steward | Draft |

## Emergency Change Rule

Emergency changes may happen before full approval only when incident stabilization requires it. They must be followed by an incident record, evidence registration, RCA or learning entry, and backlog/task/ADR/risk update before the change is considered closed.

## Quality Gate

- [ ] Every change class has review, evidence, and approval expectations.
- [ ] Code or behavior changes still require an approved task packet.
- [ ] Emergency changes produce post-change governance artifacts.
