---
type: task
status: planned
stage: execution
source_phase_task: EP4-002
source_phase_file: execution/phase-4-evolution.md
---
# TASK-1017 - Redesign cockpit around lifecycle

## Context
- [[../execution/phase-4-evolution]]
- [[TASK_INDEX]]

## Source Traceability
- Phase task: `EP4-002`
- Phase artifact: `wiki/execution/phase-4-evolution.md`
- Phase title: Phase 4 - Evolution
- Upstream dependencies: TASK-0039, TASK-0040, EP4-001

## Objective
Make cockpit show stage, blockers, next action, and responsible AI role.

## Business Reason
Owners need steering, not only dashboards.

## Technical Scope
- Lifecycle navigation and guided safe actions.

## Scope
- Lifecycle navigation and guided safe actions.

## Files to Create
- No new files expected unless the implementation instructions require a generated artifact.

## Files to Modify
- Cockpit code/docs in future tasks.
- Update cockpit docs.

## Dependencies
- TASK-0039
- TASK-0040
- EP4-001

## Implementation Instructions
1. Read `wiki/execution/phase-4-evolution.md` and locate `EP4-002` before editing.
2. Implement only this source scope: Lifecycle navigation and guided safe actions.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: Cockpit code/docs in future tasks.
5. Run the required verification: `make wiki-health`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Implementation Steps
1. Read `wiki/execution/phase-4-evolution.md` and locate `EP4-002` before editing.
2. Implement only this source scope: Lifecycle navigation and guided safe actions.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: Cockpit code/docs in future tasks.
5. Run the required verification: `make wiki-health`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Acceptance Criteria
- User always sees current stage, blockers, next action, and responsible AI role.

## Tests Required
- UI/API tests where applicable

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
- Update cockpit docs.

## Definition of Done
- [ ] TASK-1017 satisfies source phase task EP4-002.
- [ ] All acceptance criteria are met without broadening the task scope.
- [ ] Required tests and validation command pass.
- [ ] Relevant project memory and documentation are updated.
- [ ] Changed files are limited to the task scope or explicitly justified in the task notes.

## Out of Scope
- Work from later execution phase rows.
- Repository-wide refactors unrelated to this source phase task.
- New lifecycle stages, gates, or agent roles not named by this task scope.
- Implementation beyond the stated expected repository changes.
