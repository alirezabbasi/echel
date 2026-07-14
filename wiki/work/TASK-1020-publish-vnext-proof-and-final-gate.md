---
type: task
status: planned
stage: execution
source_phase_task: EP4-005
source_phase_file: execution/phase-4-evolution.md
---
# TASK-1020 - Publish vNext proof and final gate

## Context
- [[../execution/phase-4-evolution]]
- [[TASK_INDEX]]

## Source Traceability
- Phase task: `EP4-005`
- Phase artifact: `wiki/execution/phase-4-evolution.md`
- Phase title: Phase 4 - Evolution
- Upstream dependencies: TASK-0047, TASK-0048, TASK-0049, TASK-0050

## Objective
Rewrite docs, add quick start, proof pack, and final readiness gate.

## Business Reason
vNext needs auditable proof of methodology coverage.

## Technical Scope
- README, technical quick start, proof pack, final readiness gate.

## Scope
- README, technical quick start, proof pack, final readiness gate.

## Files to Create
- No new files expected unless the implementation instructions require a generated artifact.

## Files to Modify
- README/docs/proof/gate updates.
- Update release docs and proof pack.

## Dependencies
- TASK-0047
- TASK-0048
- TASK-0049
- TASK-0050

## Implementation Instructions
1. Read `wiki/execution/phase-4-evolution.md` and locate `EP4-005` before editing.
2. Implement only this source scope: README, technical quick start, proof pack, final readiness gate.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: README/docs/proof/gate updates.
5. Run the required verification: `python3 tools/echel.py doctor`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Implementation Steps
1. Read `wiki/execution/phase-4-evolution.md` and locate `EP4-005` before editing.
2. Implement only this source scope: README, technical quick start, proof pack, final readiness gate.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: README/docs/proof/gate updates.
5. Run the required verification: `python3 tools/echel.py doctor`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Acceptance Criteria
- Final gate has no critical graph issues, missing templates, command docs, evidence gaps, or unreviewed major changes.

## Tests Required
- Full verification suite

## Validation Command
```bash
python3 tools/echel.py doctor
```

## Verification Commands
```bash
python3 tools/echel.py doctor
```

## Rollback Notes
- Revert the files listed in this task if validation fails.
- Remove any generated artifacts created by this task before retrying.
- Preserve unrelated user changes and record any rollback decision in the project memory if scope or architecture changes.

## Documentation Updates
- Update release docs and proof pack.

## Definition of Done
- [ ] TASK-1020 satisfies source phase task EP4-005.
- [x] TASK-0047 README rewrite is complete.
- [x] TASK-0048 vNext technical quick start is complete.
- [ ] TASK-0049 vNext proof pack is complete.
- [ ] TASK-0050 final readiness gate is complete.
- [ ] All acceptance criteria are met without broadening the task scope.
- [ ] Required tests and validation command pass.
- [ ] Relevant project memory and documentation are updated.
- [ ] Changed files are limited to the task scope or explicitly justified in the task notes.

## Progress Notes

- 2026-07-13: TASK-0047 rewrote `README.md` around Echel as an AI-native Product-to-Repository Factory. The README now explains the discovery-to-operations lifecycle and distinguishes methodology, product memory, graph, cockpit, agents, evidence, and readiness. TASK-0048 remains responsible for the full vNext command quick start.
- 2026-07-14: TASK-0048 added the vNext technical quick start in `docs/technical-quick-start.md`. The guide now shows `discover`, `canon`, `strategy`, `requirements`, `domain`, `architecture`, `roadmap`, `plan`, `build`, `validate`, `release`, and `operate` in order, with current Echel command equivalents and regression coverage. TASK-0049 is next for proof pack coverage, and TASK-0050 remains responsible for the final readiness gate.

## Out of Scope
- Work from later execution phase rows.
- Repository-wide refactors unrelated to this source phase task.
- New lifecycle stages, gates, or agent roles not named by this task scope.
- Implementation beyond the stated expected repository changes.
