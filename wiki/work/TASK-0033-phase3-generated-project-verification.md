---
type: task
status: done
---
# TASK-0033 - Phase 3 Generated-Project Verification

## Context
- [[../reports/echel-v2-product-direction-review]]

## Objective
Add verification for Phase 3 behavior inside a generated project.

## Scope
- Initialize scratch project.
- Exercise planning, graph build, build packet, review report, next task, wiki health, and doctor.

## Out of Scope
- Browser platform testing.

## Implementation Steps
1. Add `tools/verify_phase3.py`.
2. Add `make verify-phase3`.
3. Assert packet and review artifacts contain expected sections.

## Acceptance Criteria
- [x] `make verify-phase3` exists.
- [x] Verification passes in a scratch generated project.

## Definition of Done
- Phase 3 has generated-project regression coverage.

## Verification Commands
```bash
make verify-phase3
```

## Documentation Updates
- Added generated-project verification script.
