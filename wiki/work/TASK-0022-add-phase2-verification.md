---
type: task
status: done
---
# TASK-0022 - Add Phase 2 Verification

## Objective
Add a generated-project verification loop for the Phase 2 graph workflow.

## Scope
- Initialize a scratch generated project.
- Exercise graph commands and graph-aware product commands.
- Run generated-project health checks.

## Out of Scope
- Performance or load testing.

## Implementation Steps
1. Add verification script.
2. Add Make target.
3. Exercise feature, risk, graph, plan, status, wiki health, and doctor commands.

## Context Links
- [[../reports/echel-v2-product-direction-review]]
- [[../../docs/development/phase2-product-graph]]

## Acceptance Criteria
- [x] `make verify-phase2` exists.
- [x] Phase 2 verification initializes a scratch project.
- [x] Verification exercises graph build, validation, reports, planning, status, wiki health, and doctor.

## Definition of Done
- Phase 2 verification passes in a generated project.

## Verification Commands
```bash
make verify-phase2
```

## Documentation Updates
- Added `tools/verify_phase2.py`.
