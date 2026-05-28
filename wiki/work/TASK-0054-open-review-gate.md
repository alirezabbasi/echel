---
type: task
status: done
---
# TASK-0054 - Open Review Gate

## Context
- [[../../schema/review.schema]]

## Objective
Warn when review reports are missing or include open checks.

## Scope
- Detect missing review reports.
- Detect unchecked review items.

## Out of Scope
- Automated code review.

## Implementation Steps
1. Read review reports.
2. Detect `- [ ]` checks.
3. Add readiness warnings.

## Acceptance Criteria
- [x] Missing review reports create readiness warnings.
- [x] Open review checks create readiness warnings.

## Definition of Done
- Readiness reports include review state.

## Verification Commands
```bash
make verify-phase5
```

## Documentation Updates
- Updated readiness evaluator.

