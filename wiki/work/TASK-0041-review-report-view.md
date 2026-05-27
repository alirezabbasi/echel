---
type: task
status: done
---
# TASK-0041 - Review Report View

## Context
- [[../../schema/review.schema]]

## Objective
Let users inspect review report artifacts from the cockpit.

## Scope
- List review report files.
- Connect dashboard action to `review`.

## Out of Scope
- Inline evidence registry editing.

## Implementation Steps
1. Expose review files through snapshot.
2. Render review list.
3. Add review command action.

## Acceptance Criteria
- [x] Review view exists.
- [x] Review action is available from cockpit.

## Definition of Done
- Review readiness is visible in the cockpit.

## Verification Commands
```bash
make verify-phase4
```

## Documentation Updates
- Updated cockpit UI.

