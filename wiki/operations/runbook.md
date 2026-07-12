---
type: operations-runbook
stage: operations
status: draft
owner: operations-steward
updated: 2026-07-13
---
# Runbook

## Purpose

This runbook is the primary support-facing operating guide for the product after release. It turns deployment memory, validation evidence, and engineering commands into repeatable operating procedures that a support or operations team can execute without relying on chat history.

## Source Inputs

- Deployment architecture: [[../deployment/deployment-architecture]]
- Environments: [[../deployment/environments]]
- Release process: [[../deployment/release-process]]
- Rollback plan: [[../deployment/rollback-plan]]
- Secrets management: [[../deployment/secrets-management]]
- Engineering workflow: [[../engineering/development-workflow]]
- Local development: [[../engineering/local-development]]
- Validation report: [[../validation/validation-report]]

## Operating Model

| ID | Operating Area | Owner Role | Primary Artifact | Required Action | Escalation Target | Status |
| --- | --- | --- | --- | --- | --- | --- |
| OPS-001 | Health verification | Operations Steward | `generated/product-repository/app/main.py` | Run the health check and confirm the product responds with an OK status before and after release. | Release Manager | Draft |
| OPS-002 | Validation review | QA Agent | [[../reports/validation-summary]] | Confirm latest validation summary has no open blockers before production support accepts handoff. | Release Manager | Draft |
| OPS-003 | Deployment support | Release Manager | [[../deployment/release-process]] | Follow the documented release process and record evidence for each release decision. | Governance Auditor | Draft |
| OPS-004 | Rollback support | Release Manager | [[../deployment/rollback-plan]] | Execute the matching `RB-###` rollback row when a release failure mode is detected. | Governance Auditor | Draft |
| OPS-005 | Secret handling | Security Reviewer | [[../deployment/secrets-management]] | Confirm no secret is committed and every credential class follows the allowed storage rule. | Governance Auditor | Draft |

## Routine Checks

| ID | Frequency | Check | Command Or Evidence | Expected Result | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| OPS-CHECK-001 | Before release | Syntax and test verification | `cd generated/product-repository && ./scripts/verify.sh` | Verification script exits successfully. | QA Agent | Draft |
| OPS-CHECK-002 | Before release | Release readiness | `python3 tools/echel.py readiness --stage release` | Gate passes or lists explicit blockers. | Release Manager | Draft |
| OPS-CHECK-003 | After release | Health endpoint | `python generated/product-repository/app/main.py` | Health response is visible and matches expected baseline. | Operations Steward | Draft |
| OPS-CHECK-004 | Weekly | Evidence registry review | `.echel/evidence_registry.json` | Release and validation evidence records are present and checksum-backed. | Governance Auditor | Draft |

## Support Handoff

| ID | Handoff Item | Required Source | Acceptance Signal | Owner |
| --- | --- | --- | --- | --- |
| OPS-HO-001 | Release summary | [[../roadmap/release-plan]] | Release scope, risks, and exit gates are documented. | Release Manager |
| OPS-HO-002 | Known issues | [[../validation/validation-report]] | Blockers are resolved or explicitly accepted. | QA Agent |
| OPS-HO-003 | Operating risks | [[../risks]] | Risks have mitigation or acceptance records. | Governance Auditor |
| OPS-HO-004 | Escalation path | [[incident-response]] | Severity and escalation owners are documented. | Operations Steward |

## Quality Gate

- [ ] Required deployment and engineering sources are linked.
- [ ] Routine checks include exact commands or evidence sources.
- [ ] Every operating area has an owner and escalation target.
- [ ] Support handoff identifies known risks, validation status, and escalation path.
