---
type: task
status: active
stage: execution
source_phase_task: EP4-003
source_phase_file: execution/phase-4-evolution.md
---
# TASK-1018 - Add governance integrity artifacts

## Context
- [[../execution/phase-4-evolution]]
- [[TASK_INDEX]]

## Source Traceability
- Phase task: `EP4-003`
- Phase artifact: `wiki/execution/phase-4-evolution.md`
- Phase title: Phase 4 - Evolution
- Upstream dependencies: TASK-0041, TASK-0042, TASK-0043

## Objective
Define governance docs, integrity audit, and contradiction artifacts.

## Business Reason
Long-running product memory needs visible rules and conflict resolution.

## Technical Scope
- Governance docs, `integrity audit`, contradictions artifact.

## Scope
- Governance docs, `integrity audit`, contradictions artifact.

## Files to Create
- No new files expected unless the implementation instructions require a generated artifact.

## Files to Modify
- Governance docs/commands/tests.
- Add governance docs.

## Dependencies
- TASK-0041
- TASK-0042
- TASK-0043

## Implementation Instructions
1. Read `wiki/execution/phase-4-evolution.md` and locate `EP4-003` before editing.
2. Implement only this source scope: Governance docs, `integrity audit`, contradictions artifact.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: Governance docs/commands/tests.
5. Run the required verification: `python3 tools/echel.py doctor`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Implementation Steps
1. Read `wiki/execution/phase-4-evolution.md` and locate `EP4-003` before editing.
2. Implement only this source scope: Governance docs, `integrity audit`, contradictions artifact.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: Governance docs/commands/tests.
5. Run the required verification: `python3 tools/echel.py doctor`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Acceptance Criteria
- Audit reports missing docs, stale docs, broken traceability, missing ADRs/tests/evidence; contradictions are visible and resolvable.

## Tests Required
- Unit and governance validation

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
- Add governance docs.

## Definition of Done
- [ ] TASK-1018 satisfies source phase task EP4-003.
- [x] TASK-0041 governance artifact expansion is complete.
- [ ] TASK-0042 repository integrity audit command is complete.
- [ ] TASK-0043 contradiction artifacts are complete.
- [ ] All acceptance criteria are met without broadening the task scope.
- [x] Required tests and validation command pass for TASK-0041 scope.
- [x] Relevant project memory and documentation are updated for TASK-0041.
- [x] Changed files are limited to the TASK-0041 governance-docs scope or explicitly justified in the task notes.

## Progress Notes

- 2026-07-13: TASK-0041 added `wiki/governance/documentation-governance.md`, `architecture-governance.md`, `adr-process.md`, `traceability-model.md`, `quality-gates.md`, and `repository-integrity-audit.md`. The docs make source-of-truth hierarchy, duplication rules, and deprecation process explicit, and define the future integrity audit reporting model for missing docs, stale docs, broken traceability, missing ADRs, missing tests, missing evidence, methodology violations, and contradictions.

## Out of Scope
- Work from later execution phase rows.
- Repository-wide refactors unrelated to this source phase task.
- New lifecycle stages, gates, or agent roles not named by this task scope.
- Implementation beyond the stated expected repository changes.
