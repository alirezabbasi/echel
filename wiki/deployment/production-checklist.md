---
type: deployment-artifact
stage: deployment
status: draft
owner: release
updated: 2026-07-12
---
# Production Checklist

## Purpose

This checklist is the release-stage gate input for production readiness. TASK-0036 will convert these rows into gate checks instead of relying on conversational confidence.

## Checklist

| ID | Area | Check | Required Evidence | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| PROD-001 | Validation | Validation report exists and blockers are resolved or accepted. | `wiki/validation/validation-report.md` | QA Agent | Pending |
| PROD-002 | Evidence | Release proof is registered in `.echel/evidence_registry.json`. | `EVID-###` record | QA Agent | Pending |
| PROD-003 | Deployment | Deployment path and runtime boundary are documented. | [[deployment-architecture]] | Release Manager | Pending |
| PROD-004 | Environments | Target environment and promotion rule are identified. | [[environments]] | Release Manager | Pending |
| PROD-005 | Rollback | Rollback action, owner, and verification command are documented. | [[rollback-plan]] | Release Manager | Pending |
| PROD-006 | Secrets | Secret classes, storage path, and prohibited locations are documented. | [[secrets-management]] | Security Reviewer | Pending |
| PROD-007 | Risks | Open release risks are mitigated or accepted. | `wiki/risks.md` or release report | Governance Auditor | Pending |
| PROD-008 | Operations | Operations handoff exists or is explicitly deferred. | Future `wiki/operations/runbook.md` | Operations Steward | Pending |

## Exception Rules

- An exception must name the checklist ID, reason, owner, expiration condition, and compensating control.
- Exceptions cannot hide unresolved validation blockers.
- Production readiness cannot pass with missing rollback or unknown secret handling.

## Gate Handoff

TASK-0036 should treat `Pending` rows as blockers unless the row has an accepted exception in a release readiness artifact.
