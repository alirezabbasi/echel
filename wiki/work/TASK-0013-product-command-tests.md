---
type: task
status: done
---
# TASK-0013 - Product Command Tests

## Context
- [[../project]]
- [[../reports/echel-v2-product-direction-review]]

## Objective
Add scripted verification for Phase 1 generated-project behavior.

## Scope
- Add `tools/verify_phase1.py`.
- Add `make verify-phase1`.
- Verify initialization, clarification, planning, packet generation, status, wiki health, and doctor.

## Out of Scope
- Unit test framework integration.

## Implementation Steps
1. Generate a temporary project.
2. Run product commands from generated `echel-core`.
3. Run gates.

## Acceptance Criteria
- `make verify-phase1` passes.

## Definition of Done
- Script and Make target are available.

## Verification Commands
```bash
make verify-phase1
```

## Documentation Updates
- Update Phase 1 guide.
