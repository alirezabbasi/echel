---
type: engineering-roadmap
stage: roadmap
status: draft
owner: engineering
updated: 2026-07-10
---
# Engineering Roadmap

## Purpose

The engineering roadmap identifies the implementation-enabling work needed after roadmap expansion. It keeps engineering work ordered around a usable local baseline, verification commands, documentation synchronization, and future release readiness.

## Engineering Phase Plan

| Engineering Phase | Objective | Scope | Out Of Scope | Dependencies | Demo Scenario | Risk | Exit Gate | Source IDs | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENG-001 | Execution Phase Documents | Create phase-level execution artifacts. | Foundation, MVP, hardening, production, and evolution phase docs. | RM-001, TASK-0022 | Open one phase file and see tasks, dependencies, DoD, validation, expected repo changes. | Phases do not constrain agents enough. | Every phase has validation and expected repo changes. | TASK-0022, REQ-003 | Done |
| ENG-002 | Agent Task Contract | Upgrade task generation to precise work packets. | Task fields, acceptance, tests, validation command, rollback, docs, DoD, out-of-scope. | ENG-001, TASK-0023 | Generate or inspect one task that can be implemented in one session. | Task packets omit proof obligations. | Task contract covers all TASK-0023 fields. | TASK-0023, REQ-004, REQ-006 | Done |
| ENG-003 | Repository Skeleton | Generate codebase baseline from architecture and tasks. | App/config/test/CI/env/local docs skeleton. | ENG-002, TASK-0024 | New repo structure is created and basic commands are visible. | Structure diverges from architecture. | App structure, config, tests, CI, env examples exist. | TASK-0024, ARCH-201, ARCH-202 | Done |
| ENG-004 | Engineering Documentation | Document how the generated repo is developed and verified. | Repository structure, coding standards, workflow, config strategy, local development. | ENG-003, TASK-0025 | Developer can boot locally using documented commands. | Docs become generic and not executable. | README and engineering docs include exact setup/start/lint/test commands. | TASK-0025, NFR-001 | Done |
| ENG-005 | Traceability And Graph Upgrade | Expand graph and traceability for lifecycle artifacts. | Node types, statement type, confidence, traceability matrix. | ENG-004, TASK-0029, TASK-0030, TASK-0031 | Traceability matrix shows broken chains from discovery to evidence. | Graph upgrade breaks existing graph workflows. | Existing graph validation still passes and matrix is generated. | NFR-002, TASK-0029..TASK-0031 | Done |
| ENG-006 | Validation And Evidence | Add validation command and evidence registration. | Validation artifacts, validation command, evidence add flow. | ENG-005, TASK-0032, TASK-0033, TASK-0034 | Agent registers evidence without hand-editing JSON. | Evidence remains manual and inconsistent. | Evidence records include subject, kind, path, checksum, producer, summary. | REQ-004, NFR-003, TASK-0032..TASK-0034 | Done |
| ENG-007 | Release And Operations | Add deployment, release, operations, and learning artifacts. | Deployment docs, release gate, operations docs, learning loop. | ENG-006, TASK-0035, TASK-0036, TASK-0037, TASK-0038 | Release readiness shows deployment, rollback, secrets, evidence, and open blockers. | Production readiness remains subjective. | Release gate and operations artifacts pass or block with remediation. | TASK-0035..TASK-0038, ARCH-206 | Planned |

## Engineering Guardrails

- Engineering tasks must not bypass roadmap, architecture, or requirements gates.
- Generated skeletons must include exact local verification commands.
- Documentation updates are part of the definition of done, not a later cleanup.
- Every phase must preserve product-owned `wiki/` memory and framework-core boundaries.

## Exit Criteria

- [x] Engineering work is ordered from execution planning to repository factory to validation/release.
- [x] Every phase includes demo, risk, and exit gate.
- [x] Later code-generation work depends on explicit task contracts.
- [x] Product-level engineering docs define exact setup, start, lint, test, verification, configuration, and generated-file ownership rules.
