---
type: task
status: done
stage: execution
source_phase_task: EP0-002
source_phase_file: execution/phase-0-foundation.md
---
# TASK-1002 - Define phase handoff rules

## Context
- [[../execution/phase-0-foundation]]
- [[TASK_INDEX]]

## Source Traceability
- Phase task: `EP0-002`
- Phase artifact: `wiki/execution/phase-0-foundation.md`
- Phase title: Phase 0 - Foundation
- Upstream dependencies: EP0-001

## Objective
State how roadmap phases become detailed task packets.

## Business Reason
Prevents phase documents from becoming vague backlog lists.

## Technical Scope
- Handoff rules for assumptions, blockers, validation, and owner role.

## Scope
- Handoff rules for assumptions, blockers, validation, and owner role.

## Files to Create
- No new files expected unless the implementation instructions require a generated artifact.

## Files to Modify
- wiki/execution/*.md
- docs/development/state/*.md
- self/*.md
- Update execution docs and state docs.

## Dependencies
- EP0-001

## Implementation Instructions
1. Read `wiki/execution/phase-0-foundation.md` and locate `EP0-002` before editing.
2. Implement only this source scope: Handoff rules for assumptions, blockers, validation, and owner role.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: No code; execution docs only.
5. Run the required verification: `python3 tools/echel.py graph validate`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Implementation Steps
1. Read `wiki/execution/phase-0-foundation.md` and locate `EP0-002` before editing.
2. Implement only this source scope: Handoff rules for assumptions, blockers, validation, and owner role.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: No code; execution docs only.
5. Run the required verification: `python3 tools/echel.py graph validate`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Acceptance Criteria
- Handoff rules are visible in phase docs and reference TASK-0023.

## Tests Required
- Documentation review

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
- Update execution docs and state docs.

## Definition of Done
- [x] TASK-1002 satisfies source phase task EP0-002.
- [x] All acceptance criteria are met without broadening the task scope.
- [x] Required tests and validation command pass.
- [x] Relevant project memory and documentation are updated.
- [x] Changed files are limited to the task scope or explicitly justified in the task notes.

## Out of Scope
- Work from later execution phase rows.
- Repository-wide refactors unrelated to this source phase task.
- New lifecycle stages, gates, or agent roles not named by this task scope.
- Implementation beyond the stated expected repository changes.
