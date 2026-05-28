---
type: task
status: done
---
# TASK-0048 - Release Node Support In Product Graph

## Context
- [[../../schema/product-graph.schema]]

## Objective
Extend the product graph with milestone and release nodes.

## Scope
- Add milestone/release extraction from `wiki/milestones.md`.
- Add milestone relationships to tasks and requirements.

## Out of Scope
- Fine-grained release membership editing.

## Implementation Steps
1. Add milestone writer.
2. Extract milestone and release nodes.
3. Connect milestones to work and requirements.

## Acceptance Criteria
- [x] Graph includes milestone/release nodes.
- [x] Graph validation passes after milestone creation.

## Definition of Done
- Releases are visible in product graph state.

## Verification Commands
```bash
python3 tools/echel.py graph validate
```

## Documentation Updates
- Updated graph behavior.

