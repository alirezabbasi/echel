---
type: task
status: done
---
# TASK-0039 - Graph Explorer View

## Context
- [[../reports/product-graph-report]]

## Objective
Add a readable product graph explorer to the cockpit.

## Scope
- Show graph nodes by type.
- Show graph summary and issue counts.

## Out of Scope
- Force-directed visual graph rendering.

## Implementation Steps
1. Load graph nodes from cockpit snapshot.
2. Render node browser.
3. Render graph summary.

## Acceptance Criteria
- [x] Graph explorer view exists.
- [x] Graph summary is visible.

## Definition of Done
- Product relationships are inspectable without opening JSON.

## Verification Commands
```bash
make verify-phase4
```

## Documentation Updates
- Updated cockpit UI.

