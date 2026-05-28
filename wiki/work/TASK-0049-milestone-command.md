---
type: task
status: done
---
# TASK-0049 - Milestone Command

## Context
- [[../milestones]]

## Objective
Add `echel milestone` for creating or updating milestone and release targets.

## Scope
- Name.
- Kind.
- Summary.

## Out of Scope
- Date scheduling.

## Implementation Steps
1. Add CLI parser.
2. Add milestone writer.
3. Refresh graph.

## Acceptance Criteria
- [x] `python3 tools/echel.py milestone --name "MVP"` works.
- [x] Release milestones appear in graph output.

## Definition of Done
- Product owners can declare readiness targets.

## Verification Commands
```bash
python3 tools/echel.py milestone --name "MVP" --kind release
```

## Documentation Updates
- Updated Phase 5 guide.

