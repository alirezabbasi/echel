---
type: task
status: planned
stage: execution
source_phase_task: EP3-003
source_phase_file: execution/phase-3-production.md
---
# TASK-1013 - Add evidence registration

## Context
- [[../execution/phase-3-production]]
- [[TASK_INDEX]]

## Source Traceability
- Phase task: `EP3-003`
- Phase artifact: `wiki/execution/phase-3-production.md`
- Phase title: Phase 3 - Production
- Upstream dependencies: EP3-002, TASK-0034

## Objective
Let agents register evidence without hand-editing JSON.

## Business Reason
Task closure and release proof need durable evidence records.

## Technical Scope
- `echel evidence add` flow.

## Scope
- `echel evidence add` flow.

## Files to Create
- No new files expected unless the implementation instructions require a generated artifact.

## Files to Modify
- Evidence command/tests/docs.
- Update evidence docs.

## Dependencies
- EP3-002
- TASK-0034

## Implementation Instructions
1. Read `wiki/execution/phase-3-production.md` and locate `EP3-003` before editing.
2. Implement only this source scope: `echel evidence add` flow.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: Evidence command/tests/docs.
5. Run the required verification: `python3 tools/echel.py doctor`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Implementation Steps
1. Read `wiki/execution/phase-3-production.md` and locate `EP3-003` before editing.
2. Implement only this source scope: `echel evidence add` flow.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: Evidence command/tests/docs.
5. Run the required verification: `python3 tools/echel.py doctor`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Acceptance Criteria
- Evidence includes subject, kind, path, checksum, producer, summary.

## Tests Required
- Unit tests and registry validation

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
- Update evidence docs.

## Definition of Done
- [ ] TASK-1013 satisfies source phase task EP3-003.
- [ ] All acceptance criteria are met without broadening the task scope.
- [ ] Required tests and validation command pass.
- [ ] Relevant project memory and documentation are updated.
- [ ] Changed files are limited to the task scope or explicitly justified in the task notes.

## Out of Scope
- Work from later execution phase rows.
- Repository-wide refactors unrelated to this source phase task.
- New lifecycle stages, gates, or agent roles not named by this task scope.
- Implementation beyond the stated expected repository changes.
