---
type: operations-backup-recovery
stage: operations
status: draft
owner: operations-steward
updated: 2026-07-13
---
# Backup And Recovery

## Purpose

This document defines how product memory, generated repository outputs, evidence records, and deployment state are protected and restored. It complements rollback by preserving operational continuity and auditability.

## Source Inputs

- Data architecture: [[../architecture/data-architecture]]
- Rollback plan: [[../deployment/rollback-plan]]
- Secrets management: [[../deployment/secrets-management]]
- Evidence registry: `.echel/evidence_registry.json`
- Product graph report: [[../reports/product-graph-report]]

## Protected Assets

| ID | Asset | Recovery Priority | Backup Source | Restore Method | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| BAK-001 | Product wiki memory | High | Git history and repository backup | Restore repository state or selected wiki files. | Governance Auditor | Draft |
| BAK-002 | Evidence registry | High | `.echel/evidence_registry.json` in repository workspace backup | Restore registry and verify evidence paths/checksums. | QA Agent | Draft |
| BAK-003 | Generated product repository | Medium | `generated/product-repository/` plus repository factory command | Regenerate with `python3 tools/echel.py repository-factory` or restore generated tree. | Implementation Agent | Draft |
| BAK-004 | Product graph | Medium | `wiki/graph.json` and `wiki/graph.manual.json` | Regenerate with `python3 tools/echel.py graph build`. | Governance Auditor | Draft |
| BAK-005 | Deployment and operation docs | High | Git history and repository backup | Restore `wiki/deployment/` and `wiki/operations/`. | Release Manager | Draft |

## Recovery Objectives

| ID | Scenario | Recovery Time Objective | Recovery Point Objective | Verification | Owner |
| --- | --- | --- | --- | --- | --- |
| REC-001 | Product memory corruption | Same working day | Last committed state | `make wiki-health` and graph validation. | Governance Auditor |
| REC-002 | Evidence registry corruption | Same working day | Last valid registry backup | `python3 tools/echel.py doctor` evidence section. | QA Agent |
| REC-003 | Generated repository corruption | Same working day | Last generated or committed baseline | `cd generated/product-repository && ./scripts/verify.sh`. | Implementation Agent |
| REC-004 | Release rollback | Immediate during release window | Previous release candidate | Rollback plan `RB-###` action plus release gate rerun. | Release Manager |

## Recovery Workflow

| ID | Step | Action | Evidence | Status |
| --- | --- | --- | --- | --- |
| REC-WF-001 | Identify asset | Map incident to protected asset and severity. | Incident record | Draft |
| REC-WF-002 | Choose recovery point | Select last known good commit, registry state, or generated baseline. | Decision note | Draft |
| REC-WF-003 | Restore | Restore files or regenerate deterministic artifacts. | Command output or commit reference | Draft |
| REC-WF-004 | Verify | Run the relevant validation command. | Validation or evidence record | Draft |
| REC-WF-005 | Learn | Add follow-up to evolution backlog if recovery exposed a process gap. | [[evolution-backlog]] | Draft |

## Quality Gate

- [ ] Protected assets include wiki memory, evidence, generated repo, graph, and deployment/operation docs.
- [ ] RTO/RPO expectations are documented.
- [ ] Recovery workflow includes verification and learning.
