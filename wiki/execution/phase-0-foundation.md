---
type: execution-phase
stage: execution-planning
phase: phase-0-foundation
status: draft
owner: delivery-planning
updated: 2026-07-10
---
# Phase 0 - Foundation

## Purpose

Phase 0 turns the expanded roadmap into an execution-ready foundation. It prepares the task contract, phase handoff rules, and validation baseline required before agents can receive detailed implementation tasks.

## Source Inputs

- Roadmap: [[../roadmap/master-roadmap]], [[../roadmap/mvp-roadmap]], [[../roadmap/engineering-roadmap]]
- Architecture: [[../architecture/overview]], [[../architecture/component-architecture]], [[../architecture/workflow-architecture]]
- Requirements: [[../requirements/product-requirements]], [[../requirements/acceptance-criteria]]
- Lifecycle schema: `schema/lifecycle-stage.schema.md`

## Phase Objective

Create the execution-planning foundation that TASK-0023 can use to generate agent-executable tasks without inventing scope, validation commands, rollback notes, or documentation obligations.

## Scope

- Define the task contract inputs for TASK-0023.
- Establish the execution phase handoff from roadmap to task generation.
- Preserve gate-first workflow and product-memory update obligations.
- Define validation commands that every future execution phase can cite.

## Out Of Scope

- Generating final `wiki/work/TASK-*.md` task files.
- Generating repository skeletons.
- Adding validation, deployment, or operations commands.

## Dependencies

- TASK-0021 completed expanded roadmap artifacts.
- `GATE-REQUIREMENTS`, `GATE-DOMAIN`, and `GATE-ARCHITECTURE` pass.
- Roadmap phase `RM-002` is available as the execution-planning input.

## Phase Task List

| Phase Task ID | Task | Objective | Business Reason | Scope | Dependencies | Acceptance Criteria | Tests Required | Validation Command | Documentation Updates | Expected Repo Changes | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EP0-001 | Define task contract source map | Identify which roadmap, requirement, domain, and architecture fields TASK-0023 must consume. | Agents need source-grounded tasks rather than prompt-only work. | Source map for task objective, business reason, scope, out-of-scope, dependencies, acceptance, tests, validation, rollback, docs, and DoD. | RM-002, REQ-004, ARCH-205 | Source map covers all TASK-0023 required fields. | Documentation review | `make wiki-health` | Update execution docs and methodology notes. | No code; execution docs only. | Planned |
| EP0-002 | Define phase handoff rules | State how roadmap phases become detailed task packets. | Prevents phase documents from becoming vague backlog lists. | Handoff rules for assumptions, blockers, validation, and owner role. | EP0-001 | Handoff rules are visible in phase docs and reference TASK-0023. | Documentation review | `python3 tools/echel.py graph validate` | Update execution docs and state docs. | No code; execution docs only. | Planned |
| EP0-003 | Preserve gate-first validation baseline | Require readiness checks before task generation. | Downstream task generation must not bypass lifecycle gates. | Requirements, domain, architecture, wiki health, graph validation, and unit test expectations. | GATE-REQUIREMENTS, GATE-DOMAIN, GATE-ARCHITECTURE | Future tasks cite validation commands and known doctor caveats. | Gate command review | `python3 tools/echel.py readiness --stage architecture` | Update quick start if command order changes. | No code; execution docs only. | Planned |

## Definition Of Done

- Phase task list exists with task IDs, dependencies, acceptance criteria, tests, validation command, documentation updates, and expected repo changes.
- TASK-0023 has enough context to build detailed task generation without redefining execution planning.
- Required gates and validation commands are explicit.
- No implementation task files are created prematurely.

## Validation Method

Run:

```bash
make wiki-health
python3 tools/echel.py graph validate
python3 tools/echel.py readiness --stage requirements
python3 tools/echel.py readiness --stage domain
python3 tools/echel.py readiness --stage architecture
```

## Expected Repository Changes

- `wiki/execution/phase-0-foundation.md` exists and is indexed.
- Future TASK-0023 may add or update task generation code and task templates.
- No product runtime code is expected in this phase.

## Handoff To Phase 1

Phase 1 may start when the task contract is clear enough for TASK-0023 to generate one scoped, verifiable agent task without relying on conversational context.
