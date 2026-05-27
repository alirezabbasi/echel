---
type: schema
status: active
---
# Work Packet Schema

Work packets are agent-ready implementation handoffs generated from product memory, task artifacts, and the product graph.

## File
- Path: `wiki/reports/work-packets/{TASK-id}-packet.md`
- Producer: `python3 tools/echel.py build`
- Compatibility command: `python3 tools/echel.py packet`

## Required Sections
- `Task`: human-readable task title.
- `Product Context`: project, problem, users, and solution.
- `Graph Context`: related product graph nodes.
- `Task Objective`: implementation goal.
- `Acceptance Criteria`: reviewable task expectations.
- `Evidence Obligations`: required verification and evidence duties.
- `Constraints`: implementation boundaries.
- `Verification`: commands or checks to run.
- `Required Memory Updates`: product memory updates expected after work.
- `Agent Instructions`: execution guidance.

## Review Relationship
Every work packet should be reviewable with `python3 tools/echel.py review`. Review reports are stored in `wiki/reports/reviews/`.

