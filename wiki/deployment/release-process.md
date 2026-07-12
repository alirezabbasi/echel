---
type: deployment-artifact
stage: deployment
status: draft
owner: release
updated: 2026-07-12
---
# Release Process

## Purpose

This document defines the release process from validation output to production approval. It is intentionally procedural so TASK-0036 can turn it into a deterministic release gate.

## Release Inputs

- Validation report: [[../validation/validation-report]]
- Validation summary: [[../reports/validation-summary]]
- Evidence registry: `.echel/evidence_registry.json`
- Deployment architecture: [[deployment-architecture]]
- Environment matrix: [[environments]]
- Rollback plan: [[rollback-plan]]
- Secrets management: [[secrets-management]]
- Production checklist: [[production-checklist]]

## Release Flow

| Step | Owner Role | Required Action | Evidence | Gate Behavior |
| --- | --- | --- | --- | --- |
| REL-PROC-001 | QA Agent | Run validation and summarize open risks/blockers. | `wiki/reports/validation-summary.md` | Block if validation blockers are open. |
| REL-PROC-002 | Implementation Agent | Run local and generated verification commands. | Registered command output artifact | Block if proof is missing. |
| REL-PROC-003 | Security Reviewer | Confirm no secrets are committed and secret path is documented. | Secrets checklist entry | Block if secret handling is unclear. |
| REL-PROC-004 | Release Manager | Confirm deployment path, environment, and rollback. | Deployment docs and rollback plan | Block if rollback is absent. |
| REL-PROC-005 | Governance Auditor | Review accepted risks and exceptions. | Risk or exception record | Block if risks are neither mitigated nor accepted. |
| REL-PROC-006 | Release Manager | Produce release summary and proof pack. | Release report and proof pack | Pass only when gate conditions are satisfied. |

## Approval Rules

- A release may proceed only when validation blockers are resolved or explicitly accepted.
- A release must include at least one registered evidence record for the release candidate.
- A release must state whether production, staging, CI, or local publication is the target.
- A release without rollback is not production-ready.

## Release Outputs

- Release readiness report.
- Proof pack.
- Registered evidence records.
- Updated risk state.
- Operations handoff notes.

## Handoff To Operations

Release output must tell the Operations Steward what was deployed, where it runs, how health is checked, how rollback works, and which risks or exceptions remain active.
