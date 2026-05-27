---
type: task
status: done
---
# TASK-0029 - Review Report Artifact

## Context
- [[../../schema/review.schema]]

## Objective
Generate durable review artifacts for implementation readiness.

## Scope
- Store review reports under `wiki/reports/reviews/`.
- Include pass/fail checks, missing work, graph context, and evidence references.

## Out of Scope
- Replacing human review judgment.

## Implementation Steps
1. Add review report writer.
2. Add missing-work summary.
3. Verify review output in generated projects.

## Acceptance Criteria
- [x] Review reports are generated in `wiki/reports/reviews/`.
- [x] Reports identify missing evidence and readiness gaps.

## Definition of Done
- Review state is captured as durable memory.

## Verification Commands
```bash
python3 tools/echel.py review
```

## Documentation Updates
- Added review schema.

