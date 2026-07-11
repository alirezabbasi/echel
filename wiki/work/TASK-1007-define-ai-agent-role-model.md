---
type: task
status: done
stage: execution
source_phase_task: EP2-001
source_phase_file: execution/phase-2-hardening.md
---
# TASK-1007 - Define AI agent role model

## Context
- [[../execution/phase-2-hardening]]
- [[TASK_INDEX]]

## Source Traceability
- Phase task: `EP2-001`
- Phase artifact: `wiki/execution/phase-2-hardening.md`
- Phase title: Phase 2 - Hardening
- Upstream dependencies: TASK-0026

## Objective
Describe delivery-team roles, responsibilities, inputs, outputs, and forbidden actions.

## Business Reason
Agents need bounded responsibilities to avoid uncontrolled implementation.

## Technical Scope
- Founder Interviewer through Governance Auditor roles.

## Scope
- Founder Interviewer through Governance Auditor roles.

## Files to Create
- New role model docs.

## Files to Modify
- Add role model docs.

## Dependencies
- TASK-0026

## Implementation Instructions
1. Read `wiki/execution/phase-2-hardening.md` and locate `EP2-001` before editing.
2. Implement only this source scope: Founder Interviewer through Governance Auditor roles.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: New role model docs.
5. Run the required verification: `make wiki-health`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Implementation Steps
1. Read `wiki/execution/phase-2-hardening.md` and locate `EP2-001` before editing.
2. Implement only this source scope: Founder Interviewer through Governance Auditor roles.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: New role model docs.
5. Run the required verification: `make wiki-health`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Acceptance Criteria
- Every role has responsibilities, inputs, outputs, and forbidden actions.

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
- Add role model docs.

## Definition of Done
- [x] TASK-1007 satisfies source phase task EP2-001.
- [x] All acceptance criteria are met without broadening the task scope.
- [x] Required tests and validation command pass.
- [x] Relevant project memory and documentation are updated.
- [x] Changed files are limited to the task scope or explicitly justified in the task notes.

## Out of Scope
- Work from later execution phase rows.
- Repository-wide refactors unrelated to this source phase task.
- New lifecycle stages, gates, or agent roles not named by this task scope.
- Implementation beyond the stated expected repository changes.
