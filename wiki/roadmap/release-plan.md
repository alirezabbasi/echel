---
type: release-plan
stage: roadmap
status: draft
owner: release
updated: 2026-07-10
---
# Release Plan

## Purpose

The release plan defines the milestone path implied by the roadmap. It is not the production deployment plan yet; TASK-0035 and TASK-0036 will add deployment artifacts and release gates. This document keeps the roadmap honest about what can be demonstrated, verified, and released at each milestone.

## Release Sequence

| Release ID | Milestone | Objective | Scope | Dependencies | Demo Scenario | Risk | Exit Gate | Source IDs | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REL-001 | Roadmap Artifact Release | Make architecture-to-roadmap handoff inspectable. | Five roadmap documents and compatibility summary. | TASK-0021, GATE-ARCHITECTURE | Product owner reviews roadmap and sees next action plus blockers. | Roadmap lacks executable follow-through. | Wiki health passes and roadmap docs contain phase demos, risks, and exit gates. | RM-001, TASK-0021 | Done |
| REL-002 | Execution Planning Release | Make phase planning explicit enough for AI-agent task generation. | Execution phase artifacts. | REL-001, TASK-0022 | Product owner selects next phase and sees task list, DoD, validation, repo changes. | Phase docs become mini-roadmaps instead of execution controls. | Execution phase docs meet TASK-0022 acceptance. | RM-002, TASK-0022 | Done |
| REL-003 | Agent Task Release | Make individual tasks safe for one implementation session. | Upgraded task generation and task templates. | REL-002, TASK-0023 | One task packet can be handed to an implementation agent. | Task packet misses tests or rollback. | Generated task includes all required fields and validation command. | RM-003, TASK-0023 | Planned |
| REL-004 | Repository Factory Release | Produce a runnable generated repository baseline. | App/config/test/CI/env skeleton and engineering docs. | REL-003, TASK-0024, TASK-0025 | Generated repo installs, starts, and runs tests/lint. | Skeleton cannot be verified locally. | Local development docs and verification commands pass. | RM-004, TASK-0024, TASK-0025 | Planned |
| REL-005 | Traceability Release | Make lifecycle traceability visible and auditable. | Agent roles/playbooks/handoff plus graph and traceability matrix upgrades. | REL-004, TASK-0026..TASK-0031 | Traceability report identifies complete and broken chains. | Graph metadata creates migration churn. | Graph validation passes and matrix report exists. | RM-005, TASK-0026..TASK-0031 | Planned |
| REL-006 | Validation And Operations Release | Make release readiness evidence-backed. | Validation, evidence, deployment, release, operations, learning, cockpit, governance artifacts. | REL-005, TASK-0032..TASK-0043 | Release report shows evidence, deployment posture, rollback, operations, and blockers. | Production readiness remains non-deterministic. | Release/operations/gov gates pass or report explicit blockers. | RM-006, TASK-0032..TASK-0043 | Planned |
| REL-007 | vNext Certification Release | Certify methodology coverage and generated-project readiness. | Migration, initialization, generated project verification, README/quick start/proof pack/final gate. | REL-006, TASK-0044..TASK-0050 | New project can walk through lifecycle and produce a vNext proof pack. | Backward compatibility or methodology coverage gaps remain. | Final vNext readiness gate passes or records residual risk. | RM-007, TASK-0044..TASK-0050 | Planned |

## Readiness Checkpoints

| Checkpoint | Command Or Evidence | Required Before | Owner |
| --- | --- | --- | --- |
| Architecture readiness | `python3 tools/echel.py readiness --stage architecture` | REL-001 completion and roadmap-to-execution handoff | Solution Architect |
| Wiki health | `make wiki-health` | Every roadmap and release milestone | Governance Auditor |
| Graph validation | `python3 tools/echel.py graph validate` | Milestones that change graph nodes or links | Governance Auditor |
| Unit tests | `python3 -m unittest discover -s tests` | Milestones that change tooling | QA Agent |
| Doctor report | `python3 tools/echel.py doctor` | Release confidence review, with known upstream blockers documented | Governance Auditor |

## Release Guardrails

- Do not call a roadmap release production-ready until validation, deployment, rollback, and operations artifacts exist.
- Keep known discovery gate gaps visible instead of weakening gates.
- Any release that adds command behavior must include tests and documentation updates.
- Any release that changes graph behavior must preserve graph validation.

## Exit Criteria

- [x] Release sequence starts with a usable roadmap handoff, not a deployment claim.
- [x] Each milestone has scope, dependencies, demo, risk, and exit gate.
- [x] Future production readiness depends on validation, evidence, deployment, release, and operations artifacts.
