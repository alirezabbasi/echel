---
type: task
status: planned
stage: execution
source_phase_task: EP2-004
source_phase_file: execution/phase-2-hardening.md
---
# TASK-1010 - Generate traceability matrix

## Context
- [[../execution/phase-2-hardening]]
- [[TASK_INDEX]]

## Source Traceability
- Phase task: `EP2-004`
- Phase artifact: `wiki/execution/phase-2-hardening.md`
- Phase title: Phase 2 - Hardening
- Upstream dependencies: EP2-003, TASK-0031

## Objective
Produce a report from discovery through evidence and release.

## Business Reason
Owners need impact analysis and broken-chain visibility.

## Technical Scope
- `python3 tools/echel.py traceability` and report artifact.

## Scope
- `python3 tools/echel.py traceability` and report artifact.

## Files to Create
- No new files expected unless the implementation instructions require a generated artifact.

## Files to Modify
- Traceability command and report.
- Add report docs and command docs.

## Dependencies
- EP2-003
- TASK-0031

## Implementation Instructions
1. Read `wiki/execution/phase-2-hardening.md` and locate `EP2-004` before editing.
2. Implement only this source scope: `python3 tools/echel.py traceability` and report artifact.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: Traceability command and report.
5. Run the required verification: `python3 -m unittest discover -s tests`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Implementation Steps
1. Read `wiki/execution/phase-2-hardening.md` and locate `EP2-004` before editing.
2. Implement only this source scope: `python3 tools/echel.py traceability` and report artifact.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: Traceability command and report.
5. Run the required verification: `python3 -m unittest discover -s tests`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Acceptance Criteria
- Matrix shows discovery -> canon -> strategy -> requirement -> domain -> architecture -> task -> test -> evidence and highlights broken chains.

## Tests Required
- Unit tests and report review

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
- Add report docs and command docs.

## Definition of Done
- [ ] TASK-1010 satisfies source phase task EP2-004.
- [ ] All acceptance criteria are met without broadening the task scope.
- [ ] Required tests and validation command pass.
- [ ] Relevant project memory and documentation are updated.
- [ ] Changed files are limited to the task scope or explicitly justified in the task notes.

## Out of Scope
- Work from later execution phase rows.
- Repository-wide refactors unrelated to this source phase task.
- New lifecycle stages, gates, or agent roles not named by this task scope.
- Implementation beyond the stated expected repository changes.
