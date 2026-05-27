---
type: task
status: done
---
# TASK-0042 - Risk And Decision Views

## Context
- [[../risks]]
- [[../decisions/ADR-0004-keep-product-wiki-outside-echel-core]]

## Objective
Show product risks and decisions in the cockpit.

## Scope
- Risk list.
- ADR list.

## Out of Scope
- ADR authoring workflow.

## Implementation Steps
1. Parse risk headings.
2. Parse ADR titles.
3. Render risk and decision views.

## Acceptance Criteria
- [x] Risk view exists.
- [x] Decision view exists.

## Definition of Done
- Constraints and tradeoffs are visible to product owners.

## Verification Commands
```bash
make verify-phase4
```

## Documentation Updates
- Updated cockpit UI.

