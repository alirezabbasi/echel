---
type: task
status: done
---
# TASK-0030 - Graph-Aware Next Task Selection

## Context
- [[../reports/product-graph-report]]

## Objective
Use graph signals when selecting the next open task.

## Scope
- Score open tasks using graph requirement and risk relationships.
- Preserve deterministic fallback behavior.

## Out of Scope
- ML-based prioritization.

## Implementation Steps
1. Build graph before selecting the next task.
2. Score candidate tasks by graph relationships.
3. Fall back to existing task order.

## Acceptance Criteria
- [x] `echel next` remains deterministic.
- [x] Graph relationships influence open-task selection.

## Definition of Done
- Next-task selection can use product relationship context.

## Verification Commands
```bash
python3 tools/echel.py next
```

## Documentation Updates
- Updated `tools/echel/product.py`.

