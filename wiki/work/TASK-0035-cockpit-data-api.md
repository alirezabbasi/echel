---
type: task
status: done
---
# TASK-0035 - Cockpit Data API

## Context
- [[../../schema/cockpit-api.schema]]

## Objective
Expose product status, graph, roadmap, tasks, risks, packets, reviews, and decisions through a stable local API.

## Scope
- Add cockpit snapshot service.
- Add FastAPI cockpit routes.

## Out of Scope
- Remote API authentication.

## Implementation Steps
1. Add cockpit data module.
2. Add `/api/cockpit`.
3. Verify generated-project snapshot shape.

## Acceptance Criteria
- [x] Cockpit snapshot includes required top-level keys.
- [x] API route exists in platform app.

## Definition of Done
- Cockpit data is available without hardcoding file reads into the UI.

## Verification Commands
```bash
make verify-phase4
```

## Documentation Updates
- Added cockpit API schema.

