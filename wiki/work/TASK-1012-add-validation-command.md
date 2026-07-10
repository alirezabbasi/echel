---
type: task
status: planned
stage: execution
source_phase_task: EP3-002
source_phase_file: execution/phase-3-production.md
---
# TASK-1012 - Add validation command

## Context
- [[../execution/phase-3-production]]
- [[TASK_INDEX]]

## Source Traceability
- Phase task: `EP3-002`
- Phase artifact: `wiki/execution/phase-3-production.md`
- Phase title: Phase 3 - Production
- Upstream dependencies: EP3-001, TASK-0033

## Objective
Run or summarize milestone validation.

## Business Reason
Product owners need pass/fail/skipped/blocker visibility.

## Technical Scope
- `echel validate` command and report output.

## Scope
- `echel validate` command and report output.

## Files to Create
- No new files expected unless the implementation instructions require a generated artifact.

## Files to Modify
- CLI command, tests, reports.
- Update quick start and validation docs.

## Dependencies
- EP3-001
- TASK-0033

## Implementation Instructions
1. Read `wiki/execution/phase-3-production.md` and locate `EP3-002` before editing.
2. Implement only this source scope: `echel validate` command and report output.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: CLI command, tests, reports.
5. Run the required verification: `python3 -m unittest discover -s tests`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Implementation Steps
1. Read `wiki/execution/phase-3-production.md` and locate `EP3-002` before editing.
2. Implement only this source scope: `echel validate` command and report output.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: CLI command, tests, reports.
5. Run the required verification: `python3 -m unittest discover -s tests`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Acceptance Criteria
- Reports passed, failed, skipped, risks, and blockers; adds test/evidence nodes to graph.

## Tests Required
- Unit and command tests

## Validation Command
```bash
python3 -m unittest discover -s tests
```

## Verification Commands
```bash
python3 -m unittest discover -s tests
```

## Rollback Notes
- Revert the files listed in this task if validation fails.
- Remove any generated artifacts created by this task before retrying.
- Preserve unrelated user changes and record any rollback decision in the project memory if scope or architecture changes.

## Documentation Updates
- Update quick start and validation docs.

## Definition of Done
- [ ] TASK-1012 satisfies source phase task EP3-002.
- [ ] All acceptance criteria are met without broadening the task scope.
- [ ] Required tests and validation command pass.
- [ ] Relevant project memory and documentation are updated.
- [ ] Changed files are limited to the task scope or explicitly justified in the task notes.

## Out of Scope
- Work from later execution phase rows.
- Repository-wide refactors unrelated to this source phase task.
- New lifecycle stages, gates, or agent roles not named by this task scope.
- Implementation beyond the stated expected repository changes.
