---
type: deployment-artifact
stage: deployment
status: draft
owner: release
updated: 2026-07-12
---
# Rollback Plan

## Purpose

This document defines how to recover from a failed deployment or release decision. Rollback must be planned before production readiness can pass.

## Rollback Strategy

| ID | Failure Mode | Detection Signal | Rollback Action | Data Handling | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| RB-001 | Tooling regression after lifecycle command change | Unit test, graph validation, doctor output | Revert task commit or restore previous branch | Product memory changes are reviewed before revert | Implementation Agent | Draft |
| RB-002 | Generated repository baseline fails after release | Generated `scripts/verify.sh` or CI job fails | Re-run repository factory from last good inputs or revert generated output | Preserve failing artifact as evidence | QA Agent | Draft |
| RB-003 | Documentation or gate error blocks valid release | Gate report or governance review | Correct artifact and rerun gate; do not weaken gate silently | Keep decision log entry if gate behavior changes | Governance Auditor | Draft |
| RB-004 | Future hosted deployment fails health checks | Health endpoint, logs, synthetic smoke test | Roll back to last approved release artifact | Follow backup and migration plan | Release Manager | Future |

## Rollback Preconditions

- Last known good commit or release artifact is identifiable.
- Verification command for the previous state is known.
- Any data migration or product memory mutation is reversible or explicitly accepted.
- Incident or release report records why rollback happened.

## Rollback Procedure

1. Stop promotion or deployment.
2. Capture failure evidence.
3. Identify impacted artifact family: code, generated repository, wiki memory, graph, evidence registry, or configuration.
4. Restore the last known good state.
5. Run verification commands for the restored state.
6. Register rollback evidence.
7. Update release, risk, or incident records.

## Non-Rollback Cases

- Do not roll back unrelated user changes.
- Do not delete evidence that explains the failure.
- Do not bypass gates to force a release unless an accepted exception is recorded.
