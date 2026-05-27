---
type: task
status: done
---
# TASK-0025 - Build Command Alias

## Context
- [[../roadmap]]

## Objective
Add `echel build` as the product-facing command for preparing implementation packets.

## Scope
- Add parser and handler for `build`.
- Keep `packet` available as the compatibility command.

## Out of Scope
- Direct code generation.

## Implementation Steps
1. Add CLI command.
2. Route it to work packet generation.
3. Add Make target.

## Acceptance Criteria
- [x] `python3 tools/echel.py build` generates a packet.
- [x] `make echel-build` exists.

## Definition of Done
- Product owners can ask Echel to prepare build work in product language.

## Verification Commands
```bash
python3 tools/echel.py build
```

## Documentation Updates
- Updated `README.md`.

