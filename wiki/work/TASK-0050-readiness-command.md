---
type: task
status: done
---
# TASK-0050 - Readiness Command

## Context
- [[../../schema/readiness.schema]]

## Objective
Add `echel readiness` to generate milestone/release readiness reports.

## Scope
- Evaluate graph, clarifications, work, evidence, risks, and reviews.
- Generate plain-language readiness report.

## Out of Scope
- Closing tasks automatically.

## Implementation Steps
1. Add readiness evaluator.
2. Add report generator.
3. Add CLI command.

## Acceptance Criteria
- [x] Readiness reports are generated.
- [x] Reports include blockers and next action.

## Definition of Done
- Echel can answer whether a target is ready.

## Verification Commands
```bash
python3 tools/echel.py readiness --target mvp
```

## Documentation Updates
- Added readiness schema.

