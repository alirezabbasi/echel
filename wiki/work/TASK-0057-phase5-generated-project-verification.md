---
type: task
status: done
---
# TASK-0057 - Phase 5 Generated-Project Verification

## Context
- [[../reports/echel-v2-product-direction-review]]

## Objective
Add generated-project verification for milestone readiness and proof packs.

## Scope
- Initialize scratch project.
- Generate milestone, readiness, proof pack, and release summary.
- Verify cockpit readiness data.
- Run wiki health and doctor.

## Out of Scope
- Browser automation.

## Implementation Steps
1. Add `tools/verify_phase5.py`.
2. Add `make verify-phase5`.
3. Assert generated readiness artifacts exist.

## Acceptance Criteria
- [x] `make verify-phase5` exists.
- [x] Generated-project readiness verification passes.

## Definition of Done
- Phase 5 has regression coverage.

## Verification Commands
```bash
make verify-phase5
```

## Documentation Updates
- Added Phase 5 verification script.
