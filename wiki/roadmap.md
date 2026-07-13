---
type: roadmap
status: draft
---
# Roadmap

## Expanded Roadmap Model

The vNext roadmap now lives in dedicated lifecycle artifacts:

- [[roadmap/master-roadmap]]
- [[roadmap/mvp-roadmap]]
- [[roadmap/architecture-roadmap]]
- [[roadmap/engineering-roadmap]]
- [[roadmap/release-plan]]

## Now

- Use `wiki/engineering/` as the product-owned contract for repository structure, coding, configuration, workflow, and exact local commands.
- Keep generated README, CI, and `scripts/verify.sh` synchronized through `echel repository-factory`.
- Use `wiki/agents/role-model.md` as the product-owned role contract for Echel's virtual delivery team.
- Use `prompts/playbooks/` as the canonical lifecycle prompt source for role execution.
- Use `wiki/agents/handoff-protocol.md` as the required inter-role handoff contract.
- Use `wiki/reports/traceability-matrix.md` to inspect lifecycle coverage and broken canon/evidence chains.
- Use `wiki/validation/` as the validation-stage mapping surface for requirements, tasks, domain concepts, and acceptance criteria.
- Use `python3 tools/echel.py validate` to summarize validation status and refresh graph validation nodes.
- Use `python3 tools/echel.py evidence add` to register checksum-backed proof records for task closure and release evidence.
- Use `wiki/deployment/` as the deployment-stage surface for deployment path, environments, rollback, secrets, and production checklist inputs.
- Use `python3 tools/echel.py readiness --stage release` to gate production readiness with validation, deployment, rollback, checklist, evidence, and risk checks.
- Use `wiki/operations/` as the operations-stage surface for runbook, observability, incident response, backup/recovery, SLA/SLO, change management, and evolution backlog governance.
- Use `python3 tools/echel.py learning add` to turn incidents, RCA, customer feedback, roadmap changes, and strategy changes into routed product-memory follow-ups.
- Use the cockpit lifecycle navigation to inspect Discovery through Governance stages, blockers, responsible AI roles, next actions, artifacts, and safe actions.
- Use cockpit guided actions to run native stage workflows for discovery answers, lifecycle generation, readiness, packets, validation, evidence, release reporting, learning, graph reports, and traceability.
- Use `wiki/governance/` as the governance-stage surface for source-of-truth hierarchy, duplication/deprecation rules, ADR process, traceability model, quality gates, and repository integrity audit baseline.
- Use `python3 tools/echel.py integrity audit` to report missing docs, stale docs, broken traceability, missing ADRs, missing tests, missing evidence, and methodology violations.
- Use `python3 tools/echel.py contradictions sync` to promote local contradiction records into `wiki/governance/contradictions.md`, graph nodes, and resolution tasks.
- Use `python3 tools/echel.py migration compatibility` to preserve old root wiki links while mapping them to lifecycle artifacts.
- Use updated initialization so new projects start with methodology-complete root `wiki/` lifecycle templates while Echel Core remains under `echel-core/`.

## Next

- Add the vNext technical quick start command sequence.
- Connect canon statements more fully into graph-backed traceability.

## Later

- Add operations and governance readiness gates.

## Lifecycle Compatibility

This legacy root page remains supported for old links and product-memory continuity.

- Lifecycle stage: `roadmap`
- Compatibility mode: compatibility summary
- Canonical lifecycle artifacts:
  - [[roadmap/master-roadmap]]
  - [[roadmap/mvp-roadmap]]
  - [[roadmap/release-plan]]
- Migration map: [[governance/migration-compatibility]]
