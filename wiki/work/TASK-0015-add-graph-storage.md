---
type: task
status: done
---
# TASK-0015 - Add Graph Storage

## Objective
Store generated product relationships in product-owned memory.

## Scope
- Write generated graph data into product wiki storage.
- Keep manual graph relationships separate from generated output.

## Out of Scope
- External graph persistence services.

## Implementation Steps
1. Add graph path helpers.
2. Write generated graph JSON.
3. Merge optional manual graph relationships.

## Context Links
- [[../project]]
- [[../architecture]]

## Acceptance Criteria
- [x] Graph storage path is `wiki/graph.json`.
- [x] Manual relationship storage path is `wiki/graph.manual.json`.
- [x] Storage works when tools run from generated `echel-core/`.

## Definition of Done
- Graph storage works through `WIKI_ROOT`.

## Verification Commands
```bash
python3 tools/echel.py graph build
```

## Documentation Updates
- Added graph storage behavior in `tools/echel/graph.py`.
