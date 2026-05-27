---
type: task
status: done
---
# TASK-0036 - Product Status Dashboard

## Context
- [[../project]]
- [[../reports/product-graph-report]]

## Objective
Build the cockpit dashboard for product readiness and next action.

## Scope
- Product brief.
- Clarification count.
- MVP readiness.
- Open tasks.
- Graph issue summary.
- Next action.

## Out of Scope
- Historical analytics.

## Implementation Steps
1. Read cockpit snapshot readiness.
2. Render dashboard metrics.
3. Add safe action buttons.

## Acceptance Criteria
- [x] Dashboard renders readiness and product brief.
- [x] Dashboard exposes next action and safe commands.

## Definition of Done
- The cockpit opens on product state, not chat.

## Verification Commands
```bash
make verify-phase4
```

## Documentation Updates
- Updated web UI.

