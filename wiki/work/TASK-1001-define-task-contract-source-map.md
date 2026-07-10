---
type: task
status: planned
stage: execution
source_phase_task: EP0-001
source_phase_file: execution/phase-0-foundation.md
---
# TASK-1001 - Define task contract source map

## Context
- [[../execution/phase-0-foundation]]
- [[TASK_INDEX]]

## Source Traceability
- Phase task: `EP0-001`
- Phase artifact: `wiki/execution/phase-0-foundation.md`
- Phase title: Phase 0 - Foundation
- Upstream dependencies: RM-002, REQ-004, ARCH-205

## Objective
Identify which roadmap, requirement, domain, and architecture fields TASK-0023 must consume.

## Business Reason
Agents need source-grounded tasks rather than prompt-only work.

## Technical Scope
- Source map for task objective, business reason, scope, out-of-scope, dependencies, acceptance, tests, validation, rollback, docs, and DoD.

## Scope
- Source map for task objective, business reason, scope, out-of-scope, dependencies, acceptance, tests, validation, rollback, docs, and DoD.

## Files to Create
- No new files expected unless the implementation instructions require a generated artifact.

## Files to Modify
- wiki/execution/*.md
- docs/development/state/*.md
- self/*.md
- Update execution docs and methodology notes.

## Dependencies
- RM-002
- REQ-004
- ARCH-205

## Implementation Instructions
1. Read `wiki/execution/phase-0-foundation.md` and locate `EP0-001` before editing.
2. Implement only this source scope: Source map for task objective, business reason, scope, out-of-scope, dependencies, acceptance, tests, validation, rollback, docs, and DoD.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: No code; execution docs only.
5. Run the required verification: `make wiki-health`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Implementation Steps
1. Read `wiki/execution/phase-0-foundation.md` and locate `EP0-001` before editing.
2. Implement only this source scope: Source map for task objective, business reason, scope, out-of-scope, dependencies, acceptance, tests, validation, rollback, docs, and DoD.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: No code; execution docs only.
5. Run the required verification: `make wiki-health`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Acceptance Criteria
- Source map covers all TASK-0023 required fields.

## Tests Required
- Documentation review

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
- Update execution docs and methodology notes.

## Definition of Done
- [ ] TASK-1001 satisfies source phase task EP0-001.
- [ ] All acceptance criteria are met without broadening the task scope.
- [ ] Required tests and validation command pass.
- [ ] Relevant project memory and documentation are updated.
- [ ] Changed files are limited to the task scope or explicitly justified in the task notes.

## Out of Scope
- Work from later execution phase rows.
- Repository-wide refactors unrelated to this source phase task.
- New lifecycle stages, gates, or agent roles not named by this task scope.
- Implementation beyond the stated expected repository changes.
