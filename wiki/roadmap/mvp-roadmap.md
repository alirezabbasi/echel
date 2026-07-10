---
type: mvp-roadmap
stage: roadmap
status: draft
owner: product
updated: 2026-07-10
---
# MVP Roadmap

## Purpose

The MVP roadmap defines the smallest useful Echel vNext slice after architecture readiness: an owner can move from gated requirements, domain, and architecture into execution planning and agent-ready task preparation without losing traceability or proof obligations.

## MVP Outcome

Echel vNext MVP for this phase is not a broad platform. It is a usable product-to-execution planning path:

```text
requirements gate -> domain gate -> architecture gate -> roadmap artifacts -> execution phase artifacts -> agent-executable task packets
```

## MVP Phase Plan

| MVP Step | Objective | Included Scope | Excluded Scope | Dependencies | Demo Scenario | Risk | Exit Gate | Source IDs | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MVP-RM-01 | Roadmap artifacts | Create the five roadmap documents that turn architecture into phased planning. | CLI generation, execution phases, detailed tasks. | GATE-ARCHITECTURE, TASK-0021 | Run wiki health and inspect roadmap phase map for objective, scope, dependencies, demo, risk, and exit gate. | Roadmap becomes static prose. | Five roadmap files exist and cross-reference requirements/architecture. | RM-001, REQ-003, ARCH-003 | Done |
| MVP-RM-02 | Execution phase artifacts | Create explicit phase documents for foundation, MVP, hardening, production, and evolution. | Concrete per-file implementation tasks. | MVP-RM-01, TASK-0022 | Product owner can select the next execution phase and see DoD plus validation method. | Phase documents are too broad for agents. | Each phase has task list, dependencies, DoD, validation, expected repo changes. | RM-002, TASK-0022 | Done |
| MVP-RM-03 | Task packet upgrade | Make generated tasks small, scoped, testable, and agent-executable. | Repository skeleton generation. | MVP-RM-02, TASK-0023 | Generate one task with files, tests, validation command, rollback, docs, out-of-scope, and DoD. | Task generator creates vague work. | Tasks meet the TASK-0023 contract. | RM-003, REQ-004, REQ-006 | Planned |
| MVP-RM-04 | Repository factory baseline | Generate a local repository skeleton that reflects architecture and execution tasks. | Production deployment and operations. | MVP-RM-03, TASK-0024, TASK-0025 | Generated repo installs locally, starts, runs health check, and documents lint/test commands. | Skeleton is not runnable. | Local boot and engineering docs pass. | RM-004, ARCH-201, ARCH-202 | Planned |

## MVP Demo Path

1. Run `python3 tools/echel.py readiness --stage architecture`.
2. Open [[master-roadmap]] and identify the next phase.
3. Open [[mvp-roadmap]] and confirm the smallest usable planning path.
4. Open [[architecture-roadmap]] and confirm the work preserves architecture boundaries.
5. Open [[engineering-roadmap]] and confirm the repository factory path.
6. Open [[release-plan]] and confirm readiness checkpoints before release expansion.

## MVP Exit Criteria

- [x] Roadmap artifacts define the path to usable execution planning.
- [x] MVP scope prioritizes execution safety before platform expansion.
- [x] Every MVP step has dependencies, demo, risk, and exit gate.
- [x] Execution phase artifacts exist.
- [ ] Agent-executable task format is upgraded.
- [ ] Repository factory can create a runnable local baseline.
