---
type: task
status: done
---
# TASK-0055 - Cockpit Readiness View

## Context
- [[../../schema/cockpit-api.schema]]
- [[../../schema/readiness.schema]]

## Objective
Add readiness status, blockers, proof packs, and release summaries to the cockpit.

## Scope
- Cockpit readiness snapshot.
- Readiness tab.
- Safe readiness/proof/release actions.

## Out of Scope
- Browser-based report editing.

## Implementation Steps
1. Add readiness snapshot to cockpit data.
2. Add safe cockpit actions.
3. Render readiness view in UI.

## Acceptance Criteria
- [x] Cockpit snapshot includes readiness detail.
- [x] Cockpit has readiness view and actions.

## Definition of Done
- Product owners can inspect release readiness from the cockpit.

## Verification Commands
```bash
make verify-phase5
```

## Documentation Updates
- Updated cockpit UI.

