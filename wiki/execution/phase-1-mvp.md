---
type: execution-phase
stage: execution-planning
phase: phase-1-mvp
status: draft
owner: delivery-planning
updated: 2026-07-10
---
# Phase 1 - MVP

## Purpose

Phase 1 defines the smallest executable product slice after task generation exists: a repository factory baseline that can create a local, inspectable, verifiable project skeleton from architecture and execution tasks.

## Source Inputs

- Roadmap: [[../roadmap/mvp-roadmap]], [[../roadmap/engineering-roadmap]]
- Architecture: [[../architecture/overview]], [[../architecture/data-architecture]], [[../architecture/api-architecture]], [[../architecture/security-architecture]]
- Requirements: [[../requirements/mvp-scope]], [[../requirements/non-functional-requirements]]

## Phase Objective

Produce a runnable local repository baseline with engineering documentation, exact commands, and verification expectations.

## Scope

- Repository structure generation.
- Configuration and environment examples.
- Test and CI skeletons.
- Engineering documentation for local development.

## Out Of Scope

- Production deployment.
- Release gate certification.
- Hosted orchestration or multi-project collaboration.
- Full validation and operations artifact expansion.

## Dependencies

- Phase 0 task contract foundation.
- TASK-0023 upgraded task generation.
- TASK-0024 production repository structure generator.
- TASK-0025 engineering docs templates.

## Phase Task List

| Phase Task ID | Task | Objective | Business Reason | Scope | Dependencies | Acceptance Criteria | Tests Required | Validation Command | Documentation Updates | Expected Repo Changes | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EP1-001 | Generate repository skeleton | Create the initial app, config, test, CI, and environment structure from architecture and tasks. | A product-to-repository factory must produce a usable local baseline, not only documents. | App folders, config folders, tests, CI skeleton, env examples, health check stub if applicable. | EP0-001, TASK-0023, TASK-0024 | Generated repo structure matches architecture and can be inspected locally. | Generated-project verification | `python3 tools/echel.py graph validate` | Update roadmap and engineering docs. | New repository skeleton generator outputs. | Done |
| EP1-002 | Add local development docs | Document setup, start, lint, test, and verification commands. | Users must be able to boot the generated repo without hidden context. | Repository structure, coding standards, workflow, configuration, local development docs. | EP1-001, TASK-0025 | README and engineering docs include exact commands. | Documentation and command review | `make wiki-health` | Add `wiki/engineering/*.md`. | Engineering docs under `wiki/engineering/`. | Done |
| EP1-003 | Verify MVP repository baseline | Prove generated project can run the basic local workflow. | The MVP must demonstrate usable software creation, not only planning. | Generated-project smoke verification and documented caveats. | EP1-001, EP1-002 | Setup/start/test/lint or documented placeholders are verified. | Smoke tests and generated-project verification | `python3 -m unittest discover -s tests` | Update proof or state docs. | Verification scripts or reports as needed. | Planned |

## Definition Of Done

- Generated repository baseline exists or can be generated.
- Local development docs include exact commands.
- Verification commands are documented and runnable or explicitly marked as future placeholders with rationale.
- Product-owned `wiki/` and framework-core boundaries remain intact.

## Validation Method

Run:

```bash
make wiki-health
python3 -m unittest discover -s tests
python3 tools/echel.py graph validate
```

## Expected Repository Changes

- Repository skeleton generator and generated-project verification outputs added in TASK-0024 under `generated/product-repository/`.
- Product-owned engineering documentation under `wiki/engineering/` added by TASK-0025, with generated README, CI, and verification commands synchronized through the repository factory.
- No deployment assets until release/deployment tasks begin.

## Handoff To Phase 2

Phase 2 may start from the shared engineering contract in `wiki/engineering/`. TASK-0026 must bind explicit AI-agent responsibilities and forbidden actions to that contract without duplicating it.
