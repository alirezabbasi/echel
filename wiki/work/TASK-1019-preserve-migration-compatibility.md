---
type: task
status: done
stage: execution
source_phase_task: EP4-004
source_phase_file: execution/phase-4-evolution.md
---
# TASK-1019 - Preserve migration compatibility

## Context
- [[../execution/phase-4-evolution]]
- [[TASK_INDEX]]

## Source Traceability
- Phase task: `EP4-004`
- Phase artifact: `wiki/execution/phase-4-evolution.md`
- Phase title: Phase 4 - Evolution
- Upstream dependencies: TASK-0044, TASK-0045, TASK-0046

## Objective
Map existing pages into lifecycle model and update initialization.

## Business Reason
Existing product memory must survive vNext adoption.

## Technical Scope
- Migration plan, init flow, generated project verification.

## Scope
- Migration plan, init flow, generated project verification.

## Files to Create
- No new files expected unless the implementation instructions require a generated artifact.

## Files to Modify
- Init and verification code/docs.
- Update migration/init docs.

## Dependencies
- TASK-0044
- TASK-0045
- TASK-0046

## Implementation Instructions
1. Read `wiki/execution/phase-4-evolution.md` and locate `EP4-004` before editing.
2. Implement only this source scope: Migration plan, init flow, generated project verification.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: Init and verification code/docs.
5. Run the required verification: `make wiki-health`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Implementation Steps
1. Read `wiki/execution/phase-4-evolution.md` and locate `EP4-004` before editing.
2. Implement only this source scope: Migration plan, init flow, generated project verification.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: Init and verification code/docs.
5. Run the required verification: `make wiki-health`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Acceptance Criteria
- Old pages remain usable; new projects initialize methodology-complete structure; generated project passes lifecycle checks.

## Tests Required
- Generated-project verification

## Validation Command
```bash
make wiki-health
```

## Verification Commands
```bash
make wiki-health
```

## Rollback Notes
- Revert the files listed in this task if validation fails.
- Remove any generated artifacts created by this task before retrying.
- Preserve unrelated user changes and record any rollback decision in the project memory if scope or architecture changes.

## Documentation Updates
- Update migration/init docs.

## Definition of Done
- [x] TASK-1019 satisfies source phase task EP4-004.
- [x] TASK-0044 legacy product-page migration map is complete.
- [x] TASK-0045 initialization flow update is complete.
- [x] TASK-0046 generated-project verification is complete.
- [x] All acceptance criteria are met without broadening the task scope.
- [x] Required tests and validation command pass for TASK-0044 scope.
- [x] Relevant project memory and documentation are updated for TASK-0044.
- [x] Changed files are limited to the TASK-0044 migration-compatibility scope.
- [x] Required tests and validation commands pass for TASK-0045 and TASK-0046 scope.
- [x] Relevant project memory and documentation are updated for TASK-0045 and TASK-0046.

## Progress Notes

- 2026-07-13: TASK-0044 added `python3 tools/echel.py migration compatibility`, generated `wiki/governance/migration-compatibility.md`, verified lifecycle directories, and added `Lifecycle Compatibility` sections to `wiki/project.md`, `wiki/problem.md`, `wiki/solution.md`, `wiki/scope.md`, `wiki/roadmap.md`, and `wiki/architecture.md`. TASK-0045 remains responsible for new-project initialization, and TASK-0046 remains responsible for generated-project lifecycle verification.
- 2026-07-13: TASK-0045 updated `tools/project_init.py`, `tools/init_wizard.py`, and `make init-project` so generated projects begin with methodology-complete root `wiki/` lifecycle templates while Echel Core remains under `echel-core/`. TASK-0046 remains responsible for generated-project lifecycle verification.
- 2026-07-13: TASK-0046 added `tools/verify_vnext_generated_project.py` and `make verify-vnext-generated`, proving a generated project passes lifecycle structure checks, runs representative commands from `echel-core/`, and keeps product `wiki/` outside Echel Core. TASK-1019 / EP4-004 is complete.

## Out of Scope
- Work from later execution phase rows.
- Repository-wide refactors unrelated to this source phase task.
- New lifecycle stages, gates, or agent roles not named by this task scope.
- Implementation beyond the stated expected repository changes.
