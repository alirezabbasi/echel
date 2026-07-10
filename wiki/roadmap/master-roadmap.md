---
type: master-roadmap
stage: roadmap
status: draft
owner: product
updated: 2026-07-10
---
# Master Roadmap

## Purpose

The master roadmap turns gated architecture into phased delivery without jumping directly into implementation tasks. It defines the product path from methodology-complete planning to repository factory, validation, release, operations, cockpit evolution, and governance.

Roadmap work may start only after:

- `echel readiness --stage requirements` passes;
- `echel readiness --stage domain` passes;
- `echel readiness --stage architecture` passes;
- roadmap phases cite requirements, architecture, risks, dependencies, demo scenarios, and exit gates.

## Source Inputs

- Requirements: [[../requirements/product-requirements]], [[../requirements/functional-requirements]], [[../requirements/non-functional-requirements]], [[../requirements/mvp-scope]]
- Architecture: [[../architecture/overview]], [[../architecture/component-architecture]], [[../architecture/workflow-architecture]], [[../architecture/observability-architecture]]
- Lifecycle schema: `schema/lifecycle-stage.schema.md`
- Methodology backlog: `self/Echel_Imps.md`

## Roadmap Principles

- Produce a usable product early instead of a long planning-only program.
- Keep each phase small enough to become execution-phase artifacts in TASK-0022.
- Preserve traceability from requirements and architecture into roadmap phases.
- Make every phase demonstrable, exit-gated, and safe for later AI-agent task generation.
- Do not create implementation tasks in roadmap documents; that belongs to TASK-0023.

## Phase Map

| Phase ID | Phase | Objective | Scope | Out Of Scope | Dependencies | Demo Scenario | Primary Risk | Exit Gate | Source IDs | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RM-001 | Roadmap Foundation | Establish multi-layer roadmap artifacts as the handoff from architecture to execution planning. | Master, MVP, architecture, engineering, and release roadmap documents. | Execution phase files and agent task packets. | GATE-ARCHITECTURE, ARCH-001, ARCH-002, ARCH-003 | Product owner opens roadmap docs and can identify next phase, dependencies, demo, risk, and exit gate. | Roadmap becomes another document set without execution control. | Five roadmap artifacts exist, cross-reference architecture and requirements, and pass wiki health. | TASK-0021, REQ-003, REQ-004, ARCH-003 | Done |
| RM-002 | Execution Planning MVP | Convert roadmap phases into explicit execution phase artifacts. | `wiki/execution/phase-0-foundation.md` through `phase-4-evolution.md`. | Detailed implementation tasks and repository skeleton generation. | RM-001, TASK-0022 | Product owner can see phase goals, task categories, dependencies, DoD, validation method, and expected repo changes. | Phases may be too broad for AI execution. | Every execution phase has task list, dependencies, DoD, validation, and expected repo changes. | TASK-0022, REQ-003, REQ-005, ARCH-605 | Done |
| RM-003 | Agent-Executable Task Layer | Upgrade task generation so work is safe for one AI coding session. | Task files with objective, business reason, scope, out-of-scope, files, tests, validation, rollback, docs, and DoD. | Building the repository skeleton. | RM-002, TASK-0023 | Generate one task packet that an implementation agent can execute without inventing scope. | Tasks mix unrelated concerns or miss proof obligations. | Tasks are small, traceable, testable, and include validation commands. | TASK-0023, REQ-004, REQ-006, ARCH-105 | Planned |
| RM-004 | Repository Factory Slice | Generate a bootable repository structure from architecture and execution tasks. | App, config, test, CI, environment examples, and local development docs. | Production deployment and operations runbooks. | RM-003, TASK-0024, TASK-0025 | A generated product repo can install, start, run tests, and explain its local workflow. | Skeleton diverges from architecture or cannot run locally. | Local boot, health check, lint/test commands, and engineering docs exist. | TASK-0024, TASK-0025, ARCH-201, ARCH-202 | Planned |
| RM-005 | Orchestration And Traceability | Add role model, playbooks, handoff protocol, graph expansion, confidence, and traceability matrix. | Agent roles, lifecycle playbooks, handoffs, graph node types, statement metadata, traceability report. | Validation, release, and operations gates. | RM-004, TASK-0026, TASK-0027, TASK-0028, TASK-0029, TASK-0030, TASK-0031 | A product owner can trace discovery to architecture and hand off work between AI roles with explicit assumptions and risks. | Role/playbook system becomes prompt duplication. | Traceability matrix highlights broken chains and graph reflects lifecycle artifacts. | TASK-0026..TASK-0031, NFR-002, ARCH-204 | Planned |
| RM-006 | Validation Release Operations | Add validation, evidence, deployment, release, operations, learning, cockpit vNext, and governance integrity. | Validation docs/command, evidence registration, deployment artifacts, release gate, operations docs, learning loop, cockpit lifecycle views, governance audit. | Rewriting completed lifecycle artifacts without reason. | RM-005, TASK-0032..TASK-0043 | Product owner can see validation status, release readiness, operational posture, and governance blockers. | Release confidence remains document-based instead of evidence-based. | Release/operations gates pass or show concrete blockers with evidence. | TASK-0032..TASK-0043, REQ-004, NFR-003, ARCH-206 | Planned |
| RM-007 | vNext Packaging And Proof | Migrate existing pages, update initialization, verify generated projects, and publish vNext proof. | Migration compatibility, initialization flow, full generated-project verification, README/quick start/proof pack/final readiness. | New methodology scope beyond TASK-0050. | RM-006, TASK-0044..TASK-0050 | A new product can be initialized and walked through the lifecycle with proof of methodology coverage. | Backward compatibility breaks existing product memory. | Final vNext readiness gate passes or reports residual risks. | TASK-0044..TASK-0050, ADR-0004, ADR-0005 | Planned |

## Roadmap Exit Gate

- [x] Architecture readiness passes before roadmap creation.
- [x] Every roadmap phase has objective, scope, dependencies, demo scenario, risk, and exit gate.
- [x] MVP path produces usable product behavior before late-stage platform expansion.
- [x] Execution planning remains separate from detailed implementation tasks.
- [x] Root roadmap compatibility summary points to the expanded roadmap artifacts.
