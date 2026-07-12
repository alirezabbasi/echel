---
type: operations-observability
stage: operations
status: draft
owner: operations-steward
updated: 2026-07-13
---
# Observability

## Purpose

This document defines the signals operators need to understand product health, release safety, and support impact. It extends the architecture observability model into production operating memory.

## Source Inputs

- Observability architecture: [[../architecture/observability-architecture]]
- Validation summary: [[../reports/validation-summary]]
- Runbook: [[runbook]]
- Incident response: [[incident-response]]

## Signal Inventory

| ID | Signal | Product Question | Source | Collection Method | Alert Condition | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OBS-001 | Health check result | Is the generated product baseline reachable? | `generated/product-repository/app/main.py` | Manual or scripted health run. | Health response is missing or malformed. | Operations Steward | Draft |
| OBS-002 | Verification result | Does the release candidate still satisfy local checks? | `generated/product-repository/scripts/verify.sh` | Run before release and after rollback. | Script exits non-zero. | QA Agent | Draft |
| OBS-003 | Validation blockers | Are validation blockers present? | [[../validation/validation-report]] | `python3 tools/echel.py validate` | Any blocker remains open. | QA Agent | Draft |
| OBS-004 | Release gate result | Is production readiness blocked? | `python3 tools/echel.py readiness --stage release` | Gate run before release review. | Gate reports blocked. | Release Manager | Draft |
| OBS-005 | Evidence freshness | Is proof recent and checksum-backed? | `.echel/evidence_registry.json` | Evidence registry inspection. | Required release evidence missing or stale. | Governance Auditor | Draft |

## Dashboards And Reports

| ID | View | Audience | Required Signals | Update Trigger | Status |
| --- | --- | --- | --- | --- | --- |
| OBS-VIEW-001 | Release readiness review | Release Manager, Governance Auditor | OBS-003, OBS-004, OBS-005 | Before production release decision. | Draft |
| OBS-VIEW-002 | Support health review | Operations Steward | OBS-001, OBS-002 | After release or incident. | Draft |
| OBS-VIEW-003 | Validation review | QA Agent | OBS-002, OBS-003 | Before evidence registration. | Draft |

## Alert Routing

| ID | Condition | Severity | First Responder | Escalation | Response Artifact |
| --- | --- | --- | --- | --- | --- |
| OBS-ALERT-001 | Health check unavailable after release | SEV-2 | Operations Steward | Release Manager | [[incident-response]] |
| OBS-ALERT-002 | Verification script fails before release | SEV-3 | QA Agent | Release Manager | [[../validation/validation-report]] |
| OBS-ALERT-003 | Release gate blocked | SEV-3 | Release Manager | Governance Auditor | [[../deployment/production-checklist]] |
| OBS-ALERT-004 | Evidence checksum missing or invalid | SEV-3 | Governance Auditor | QA Agent | `.echel/evidence_registry.json` |

## Quality Gate

- [ ] Every operational signal has a source, collection method, owner, and alert condition.
- [ ] Release, support, and validation views are defined.
- [ ] Alert routing references incident or validation artifacts.
