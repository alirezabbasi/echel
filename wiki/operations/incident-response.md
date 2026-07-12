---
type: operations-incident-response
stage: operations
status: draft
owner: operations-steward
updated: 2026-07-13
---
# Incident Response

## Purpose

This document defines severity, escalation, and response workflow for production or release incidents. It ensures incidents become structured product memory instead of disappearing into chat or ad hoc fixes.

## Source Inputs

- Runbook: [[runbook]]
- Observability: [[observability]]
- Rollback plan: [[../deployment/rollback-plan]]
- Change management: [[change-management]]
- Evolution backlog: [[evolution-backlog]]

## Severity Model

| ID | Severity | Definition | Customer Impact | Response Time Target | Escalation Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SEV-1 | Critical | Product is unavailable, data integrity is at risk, or release created a severe safety issue. | High | Immediate response. | Governance Auditor | Draft |
| SEV-2 | High | Core workflow is degraded or release validation missed a serious defect. | Medium to high | Same working day. | Release Manager | Draft |
| SEV-3 | Medium | Non-critical workflow issue, failed operational check, or blocked readiness gate. | Medium | Next planned support window. | Operations Steward | Draft |
| SEV-4 | Low | Documentation gap, minor usability issue, or improvement request. | Low | Backlog triage. | Product Manager | Draft |

## Escalation Matrix

| ID | Trigger | First Responder | Escalates To | Required Artifact | Status |
| --- | --- | --- | --- | --- | --- |
| INC-ESC-001 | SEV-1 declared | Operations Steward | Governance Auditor | Incident record and rollback decision | Draft |
| INC-ESC-002 | SEV-2 release regression | Release Manager | Governance Auditor | Rollback or forward-fix decision | Draft |
| INC-ESC-003 | Security or secret handling concern | Security Reviewer | Governance Auditor | Security review note | Draft |
| INC-ESC-004 | Repeated SEV-3 operational check failure | Operations Steward | Product Manager | Evolution backlog item | Draft |

## Response Workflow

| ID | Step | Action | Owner | Output Artifact | Status |
| --- | --- | --- | --- | --- | --- |
| INC-WF-001 | Detect | Confirm signal from observability, validation, support report, or release gate output. | Operations Steward | Incident record | Draft |
| INC-WF-002 | Classify | Assign severity using the severity model. | Operations Steward | Incident record | Draft |
| INC-WF-003 | Stabilize | Use the runbook and rollback plan to stop customer or product impact. | Release Manager | Rollback or mitigation note | Draft |
| INC-WF-004 | Communicate | Record current state, owner, impact, and next update. | Operations Steward | Support update | Draft |
| INC-WF-005 | Learn | Create RCA and route follow-up to evolution backlog, ADR, risk, assumption, or task. | Governance Auditor | Learning artifact | Draft |

## Incident Record Template

| Field | Required Content |
| --- | --- |
| Incident ID | `INC-###` |
| Severity | `SEV-1` through `SEV-4` |
| Detected by | Signal, customer, agent, or operator |
| Impact | Users, workflows, data, release, or evidence affected |
| Timeline | Detection, escalation, mitigation, resolution |
| Root cause | Known cause or investigation status |
| Follow-up | Evolution backlog, task, ADR, risk, or assumption link |

## Quality Gate

- [ ] Severity definitions and response targets exist.
- [ ] Escalation owners are explicit.
- [ ] Response workflow produces durable artifacts.
- [ ] Learning follow-up routes to governed product memory.
