---
type: task
status: done
---
# TASK-0038 - Roadmap And Work Queue View

## Context
- [[../roadmap]]

## Objective
Show roadmap sections and work queue in the cockpit.

## Scope
- Roadmap now, MVP, next, and later sections.
- Task list with status and objective.

## Out of Scope
- Drag-and-drop planning.

## Implementation Steps
1. Parse roadmap sections.
2. Parse task artifacts.
3. Render roadmap and work views.

## Acceptance Criteria
- [x] Roadmap view exists.
- [x] Work queue view exists.

## Definition of Done
- Product direction and work are visible together.

## Verification Commands
```bash
make verify-phase4
```

## Documentation Updates
- Updated cockpit UI.

