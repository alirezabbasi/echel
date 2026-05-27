---
type: task
status: done
---
# TASK-0026 - Review Command

## Context
- [[../../schema/review.schema]]

## Objective
Add `echel review` for evaluating work against acceptance criteria, evidence expectations, and graph integrity.

## Scope
- Generate review reports.
- Include graph context, graph issues, evidence references, and missing work.

## Out of Scope
- Automatic task closure.

## Implementation Steps
1. Add review report generation.
2. Add CLI command and Make target.
3. Verify in generated projects.

## Acceptance Criteria
- [x] `python3 tools/echel.py review` writes a review report.
- [x] Review report includes checks and recommended next action.

## Definition of Done
- Work can be reviewed before closure.

## Verification Commands
```bash
python3 tools/echel.py review
```

## Documentation Updates
- Added `schema/review.schema.md`.

