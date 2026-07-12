---
type: execution-phase
stage: execution-planning
phase: phase-3-production
status: draft
owner: release
updated: 2026-07-10
---
# Phase 3 - Production

## Purpose

Phase 3 adds validation, evidence, deployment, release, and operations artifacts so Echel can evaluate production readiness with proof instead of confidence from documentation alone.

## Source Inputs

- Roadmap: [[../roadmap/release-plan]], [[../roadmap/engineering-roadmap]]
- Architecture: [[../architecture/security-architecture]], [[../architecture/observability-architecture]], [[../architecture/data-architecture]]
- Requirements: [[../requirements/acceptance-criteria]], [[../requirements/non-functional-requirements]]

## Phase Objective

Make release readiness evidence-backed, deployment-aware, and operationally inspectable.

## Scope

- Validation strategy artifacts.
- Validation command.
- Evidence registration.
- Deployment artifact templates.
- Release gate.
- Operations artifact templates.

## Out Of Scope

- Post-release learning automation beyond planned hooks.
- Cockpit lifecycle redesign.
- Migration and final vNext release packaging.

## Dependencies

- Phase 2 graph and traceability hardening.
- TASK-0032 through TASK-0037.
- Evidence and release readiness architecture remains local-first unless future ADRs justify escalation.

## Phase Task List

| Phase Task ID | Task | Objective | Business Reason | Scope | Dependencies | Acceptance Criteria | Tests Required | Validation Command | Documentation Updates | Expected Repo Changes | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EP3-001 | Add validation artifacts | Define test strategy, acceptance, integration, e2e, security, performance, and validation report docs. | Release confidence requires mapped tests and validation reporting. | `wiki/validation/*.md` templates. | TASK-0032, EP2-004 | Tests map to requirement IDs, task IDs, domain concepts, and acceptance criteria. | Documentation review | `make wiki-health` | Add validation docs. | Validation artifact files. | Done |
| EP3-002 | Add validation command | Run or summarize milestone validation. | Product owners need pass/fail/skipped/blocker visibility. | `echel validate` command and report output. | EP3-001, TASK-0033 | Reports passed, failed, skipped, risks, and blockers; adds test/evidence nodes to graph. | Unit and command tests | `python3 -m unittest discover -s tests` | Update quick start and validation docs. | CLI command, tests, reports. | Done |
| EP3-003 | Add evidence registration | Let agents register evidence without hand-editing JSON. | Task closure and release proof need durable evidence records. | `echel evidence add` flow. | EP3-002, TASK-0034 | Evidence includes subject, kind, path, checksum, producer, summary. | Unit tests and registry validation | `python3 tools/echel.py doctor` | Update evidence docs. | Evidence command/tests/docs. | Done |
| EP3-004 | Add deployment and release gates | Create deployment artifacts and production release readiness gate. | Deployment, rollback, secrets, and blockers must be evaluated before production. | Deployment docs and release gate checks. | TASK-0035, TASK-0036 | Deployment path, rollback, secrets, checklist, evidence, risks, and blockers are gated. | Gate tests and docs review | `python3 tools/echel.py doctor` | Add deployment and release docs. | Deployment docs, gate code/tests. | Planned |
| EP3-005 | Add operations artifacts | Create operation docs for support, incidents, backup, SLO, change, and evolution backlog. | Production systems need maintainable operations memory. | `wiki/operations/*.md` templates. | TASK-0037 | Support team can operate product; severity/escalation and evolution backlog are governed. | Documentation review | `make wiki-health` | Add operations docs. | Operations artifact files. | Planned |

## Definition Of Done

- Validation artifacts map tests to requirements and acceptance criteria.
- Evidence registration is deterministic and auditable.
- Deployment and release readiness have explicit blockers.
- Operations artifacts define support, incident, backup, SLO, and change responsibilities.

## Progress Notes

- 2026-07-12: TASK-0035 completed the deployment artifact templates for EP3-004. The phase row remains Planned until TASK-0036 implements release gate checks.

## Validation Method

Run:

```bash
make wiki-health
python3 -m unittest discover -s tests
python3 tools/echel.py graph validate
python3 tools/echel.py doctor
```

## Expected Repository Changes

- Validation, deployment, and operations documentation.
- New validation/evidence/release commands and tests in future tasks.
- Gate policy updates when release readiness becomes executable.

## Handoff To Phase 4

Phase 4 may start once production readiness can be evaluated through validation reports, evidence records, deployment checks, and operations artifacts.
