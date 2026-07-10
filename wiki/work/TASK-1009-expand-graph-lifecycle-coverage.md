---
type: task
status: planned
stage: execution
source_phase_task: EP2-003
source_phase_file: execution/phase-2-hardening.md
---
# TASK-1009 - Expand graph lifecycle coverage

## Context
- [[../execution/phase-2-hardening]]
- [[TASK_INDEX]]

## Source Traceability
- Phase task: `EP2-003`
- Phase artifact: `wiki/execution/phase-2-hardening.md`
- Phase title: Phase 2 - Hardening
- Upstream dependencies: TASK-0029, TASK-0030

## Objective
Add lifecycle node types and graph metadata for statement type, confidence, source stage, and verification status.

## Business Reason
AI must distinguish facts from assumptions and trace lifecycle chains.

## Technical Scope
- Discovery, assumption, strategy, domain, architecture, test, deployment, operations, contradiction, and learning nodes.

## Scope
- Discovery, assumption, strategy, domain, architecture, test, deployment, operations, contradiction, and learning nodes.

## Files to Create
- No new files expected unless the implementation instructions require a generated artifact.

## Files to Modify
- Graph code/tests/schema updates.
- Update graph docs and traceability docs.

## Dependencies
- TASK-0029
- TASK-0030

## Implementation Instructions
1. Read `wiki/execution/phase-2-hardening.md` and locate `EP2-003` before editing.
2. Implement only this source scope: Discovery, assumption, strategy, domain, architecture, test, deployment, operations, contradiction, and learning nodes.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: Graph code/tests/schema updates.
5. Run the required verification: `python3 tools/echel.py graph validate`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Implementation Steps
1. Read `wiki/execution/phase-2-hardening.md` and locate `EP2-003` before editing.
2. Implement only this source scope: Discovery, assumption, strategy, domain, architecture, test, deployment, operations, contradiction, and learning nodes.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: Graph code/tests/schema updates.
5. Run the required verification: `python3 tools/echel.py graph validate`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Acceptance Criteria
- Graph validation passes and nodes carry required metadata where available.

## Tests Required
- Unit and graph tests

## Validation Command
```bash
python3 tools/echel.py graph validate
```

## Verification Commands
```bash
python3 tools/echel.py graph validate
```

## Rollback Notes
- Revert the files listed in this task if validation fails.
- Remove any generated artifacts created by this task before retrying.
- Preserve unrelated user changes and record any rollback decision in the project memory if scope or architecture changes.

## Documentation Updates
- Update graph docs and traceability docs.

## Definition of Done
- [ ] TASK-1009 satisfies source phase task EP2-003.
- [ ] All acceptance criteria are met without broadening the task scope.
- [ ] Required tests and validation command pass.
- [ ] Relevant project memory and documentation are updated.
- [ ] Changed files are limited to the task scope or explicitly justified in the task notes.

## Out of Scope
- Work from later execution phase rows.
- Repository-wide refactors unrelated to this source phase task.
- New lifecycle stages, gates, or agent roles not named by this task scope.
- Implementation beyond the stated expected repository changes.
