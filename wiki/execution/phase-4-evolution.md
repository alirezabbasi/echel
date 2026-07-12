---
type: execution-phase
stage: execution-planning
phase: phase-4-evolution
status: draft
owner: governance
updated: 2026-07-13
---
# Phase 4 - Evolution

## Purpose

Phase 4 turns Echel from a gated delivery system into a continuously improving AI-native product operating system. It adds learning loops, lifecycle cockpit behavior, governance integrity, migration support, generated-project verification, and final vNext proof.

## Source Inputs

- Roadmap: [[../roadmap/master-roadmap]], [[../roadmap/release-plan]]
- Architecture: [[../architecture/observability-architecture]], [[../architecture/component-architecture]]
- Operations artifacts from Phase 3.

## Phase Objective

Make product evolution visible, governed, and repeatable across future projects without breaking existing product memory.

## Scope

- Learning loop.
- Cockpit lifecycle views and guided actions.
- Governance artifact expansion.
- Repository integrity audit.
- Contradiction artifacts.
- Migration and backward compatibility.
- Initialization update.
- Generated project verification.
- vNext documentation, proof pack, and final readiness gate.

## Out Of Scope

- Adding new lifecycle stages beyond TASK-0050.
- Replacing existing product memory without migration rules.
- Hosted enterprise runtime unless future ADRs require it.

## Dependencies

- Phase 3 production readiness artifacts.
- TASK-0038 through TASK-0050.
- Existing root wiki pages remain usable through migration compatibility.

## Phase Task List

| Phase Task ID | Task | Objective | Business Reason | Scope | Dependencies | Acceptance Criteria | Tests Required | Validation Command | Documentation Updates | Expected Repo Changes | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EP4-001 | Add learning loop | Connect incidents, RCA, customer feedback, roadmap changes, and strategy updates to memory. | Product intelligence must improve after release. | Learning command/artifacts and update paths. | TASK-0038, Phase 3 operations docs | Learnings can create tasks, ADRs, risks, assumptions, or strategy changes. | Unit and docs review | `python3 -m unittest discover -s tests` | Add learning docs. | Learning artifacts/command. | Done |
| EP4-002 | Redesign cockpit around lifecycle | Make cockpit show stage, blockers, next action, and responsible AI role. | Owners need steering, not only dashboards. | Lifecycle navigation and guided safe actions. | TASK-0039, TASK-0040, EP4-001 | User always sees current stage, blockers, next action, and responsible AI role. | UI/API tests where applicable | `make wiki-health` | Update cockpit docs. | Cockpit code/docs in future tasks. | In Progress |
| EP4-003 | Add governance integrity artifacts | Define governance docs, integrity audit, and contradiction artifacts. | Long-running product memory needs visible rules and conflict resolution. | Governance docs, `integrity audit`, contradictions artifact. | TASK-0041, TASK-0042, TASK-0043 | Audit reports missing docs, stale docs, broken traceability, missing ADRs/tests/evidence; contradictions are visible and resolvable. | Unit and governance validation | `python3 tools/echel.py doctor` | Add governance docs. | Governance docs/commands/tests. | Planned |
| EP4-004 | Preserve migration compatibility | Map existing pages into lifecycle model and update initialization. | Existing product memory must survive vNext adoption. | Migration plan, init flow, generated project verification. | TASK-0044, TASK-0045, TASK-0046 | Old pages remain usable; new projects initialize methodology-complete structure; generated project passes lifecycle checks. | Generated-project verification | `make wiki-health` | Update migration/init docs. | Init and verification code/docs. | Planned |
| EP4-005 | Publish vNext proof and final gate | Rewrite docs, add quick start, proof pack, and final readiness gate. | vNext needs auditable proof of methodology coverage. | README, technical quick start, proof pack, final readiness gate. | TASK-0047, TASK-0048, TASK-0049, TASK-0050 | Final gate has no critical graph issues, missing templates, command docs, evidence gaps, or unreviewed major changes. | Full verification suite | `python3 tools/echel.py doctor` | Update release docs and proof pack. | README/docs/proof/gate updates. | Planned |

## Definition Of Done

- Learning, cockpit, governance, migration, and final readiness work are sequenced.
- Backward compatibility is explicit before initialization changes.
- Final vNext proof depends on generated-project verification and governance gates.
- No future phase hides unresolved discovery, evidence, or graph blockers.

## Progress Notes

- 2026-07-13: TASK-0038 completed EP4-001. `python3 tools/echel.py learning add` now captures incidents, RCA, feedback, roadmap changes, and strategy changes into operations learning records and routes follow-up to tasks, ADRs, risks, assumptions, or strategy-change artifacts.
- 2026-07-13: TASK-0039 completed the lifecycle navigation portion of EP4-002. Cockpit snapshot and UI now expose Discovery through Governance stages, current stage, blockers, next action, responsible AI role, artifacts, and command-backed safe action metadata. TASK-0040 remains responsible for deeper native guided actions per stage.

## Validation Method

Run:

```bash
make wiki-health
python3 -m unittest discover -s tests
python3 tools/echel.py graph validate
python3 tools/echel.py doctor
```

## Expected Repository Changes

- Learning, cockpit, governance, migration, initialization, proof-pack, and final-readiness artifacts.
- Future command and cockpit code changes with tests.
- Updated README and quick start when vNext release packaging begins.

## Handoff To Continuous Evolution

After Phase 4, Echel should be able to initialize new methodology-complete projects, verify generated projects, report lifecycle readiness, and evolve through governed learning rather than ad hoc documentation edits.
