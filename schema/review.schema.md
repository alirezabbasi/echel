---
type: schema
status: active
---
# Review Report Schema

Review reports evaluate whether an implementation is ready for closure against product memory, graph integrity, acceptance criteria, and evidence expectations.

## File
- Path: `wiki/reports/reviews/{TASK-id}-review.md`
- Producer: `python3 tools/echel.py review`

## Required Sections
- `Task`: task under review.
- `Outcome`: current closure readiness summary.
- `Review Checks`: checklist of required review signals.
- `Graph Context`: related product graph nodes.
- `Graph Issues`: graph validation findings.
- `Evidence`: evidence IDs referenced by the task.
- `Missing Work`: unchecked review items.
- `Recommended Next Action`: closure or remediation guidance.

## Closure Rule
Review reports are advisory. Task closure remains enforced by `python3 tools/echel.py close-task`, which requires registered evidence IDs.

