---
type: task
status: done
stage: execution
source_phase_task: EP2-002
source_phase_file: execution/phase-2-hardening.md
---
# TASK-1008 - Add lifecycle playbooks and handoff protocol

## Context
- [[../execution/phase-2-hardening]]
- [[TASK_INDEX]]

## Source Traceability
- Phase task: `EP2-002`
- Phase artifact: `wiki/execution/phase-2-hardening.md`
- Phase title: Phase 2 - Hardening
- Upstream dependencies: EP2-001, TASK-0027, TASK-0028

## Objective
Replace duplicated prompt packs with canonical stage playbooks and handoff summaries.

## Business Reason
Handoffs should preserve assumptions, risks, unresolved questions, and next-stage instructions.

## Technical Scope
- Playbooks for lifecycle stages and handoff protocol.

## Scope
- Playbooks for lifecycle stages and handoff protocol.

## Files to Create
- Prompt/playbook and handoff files.

## Files to Modify
- Add `prompts/playbooks/*.md` and handoff docs.

## Dependencies
- EP2-001
- TASK-0027
- TASK-0028

## Implementation Instructions
1. Read `wiki/execution/phase-2-hardening.md` and locate `EP2-002` before editing.
2. Implement only this source scope: Playbooks for lifecycle stages and handoff protocol.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: Prompt/playbook and handoff files.
5. Run the required verification: `make wiki-health`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Implementation Steps
1. Read `wiki/execution/phase-2-hardening.md` and locate `EP2-002` before editing.
2. Implement only this source scope: Playbooks for lifecycle stages and handoff protocol.
3. Keep the task focused on one concern; split follow-up work into a new task if unrelated scope appears.
4. Apply the expected repository change: Prompt/playbook and handoff files.
5. Run the required verification: `make wiki-health`.
6. Update the documentation listed in this task and record any new architectural decision only if one was actually made.

## Acceptance Criteria
- Tool-specific prompts can render from canonical playbooks; handoffs include required fields.

## Tests Required
- Documentation and prompt review

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
- Add `prompts/playbooks/*.md` and handoff docs.

## Definition of Done
- [x] TASK-1008 satisfies source phase task EP2-002.
- [x] All acceptance criteria are met without broadening the task scope.
- [x] Required tests and validation command pass.
- [x] Relevant project memory and documentation are updated.
- [x] Changed files are limited to the task scope or explicitly justified in the task notes.

## Out of Scope
- Work from later execution phase rows.
- Repository-wide refactors unrelated to this source phase task.
- New lifecycle stages, gates, or agent roles not named by this task scope.
- Implementation beyond the stated expected repository changes.
