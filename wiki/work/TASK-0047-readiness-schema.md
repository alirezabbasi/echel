---
type: task
status: done
---
# TASK-0047 - Readiness Schema

## Context
- [[../../schema/readiness.schema]]

## Objective
Add a schema for readiness report structure and readiness gates.

## Scope
- Required sections.
- Readiness states.
- Blocking conditions.

## Out of Scope
- JSON schema validation.

## Implementation Steps
1. Add readiness schema doc.
2. Align generated readiness report sections.

## Acceptance Criteria
- [x] Readiness schema exists.
- [x] Generated readiness reports follow the documented shape.

## Definition of Done
- Readiness artifacts are documented for agents and maintainers.

## Verification Commands
```bash
make wiki-health
```

## Documentation Updates
- Added `schema/readiness.schema.md`.

