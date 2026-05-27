---
type: task
status: done
---
# TASK-0045 - Phase 4 Generated-Project Verification

## Context
- [[../reports/echel-v2-product-direction-review]]

## Objective
Add generated-project verification for the cockpit data and command surface.

## Scope
- Initialize scratch project.
- Exercise plan, build, review, platform init, cockpit snapshot, safe command bridge, wiki health, and doctor.

## Out of Scope
- Browser automation.

## Implementation Steps
1. Add `tools/verify_phase4.py`.
2. Add `make verify-phase4`.
3. Validate cockpit snapshot shape and command bridge.

## Acceptance Criteria
- [x] `make verify-phase4` exists.
- [x] Generated-project cockpit verification passes.

## Definition of Done
- Phase 4 has regression coverage.

## Verification Commands
```bash
make verify-phase4
```

## Documentation Updates
- Added Phase 4 verification script.
