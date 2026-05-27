---
type: task
status: done
---
# TASK-0020 - Add Relationship Commands

## Objective
Add command-line operations for adding features, risks, and manual graph relationships.

## Scope
- Add feature creation command.
- Add risk creation command.
- Add manual relationship command.

## Out of Scope
- Rich interactive graph editor.

## Implementation Steps
1. Add feature command parser and handler.
2. Add risk command parser and handler.
3. Add manual link command parser and handler.

## Context Links
- [[../solution]]
- [[../risks]]

## Acceptance Criteria
- [x] `echel feature add` updates product capabilities.
- [x] `echel risk add` records product risks.
- [x] `echel link` records manual graph relationships.

## Definition of Done
- Relationship commands update product-owned wiki files.

## Verification Commands
```bash
python3 tools/echel.py feature add --title "Product memory graph"
python3 tools/echel.py risk add --title "Ambiguous requirements" --mitigation "Validate work through the graph."
```

## Documentation Updates
- Added feature, risk, and link commands in `tools/echel.py`.
