---
type: guide
status: active
---
# Phase 3 Agent Work Packets

Phase 3 turns graph-backed product memory into reliable agent handoffs and review reports.

## Command Flow
```bash
python3 tools/echel.py plan
python3 tools/echel.py graph build
python3 tools/echel.py build
python3 tools/echel.py review
python3 tools/echel.py graph validate
python3 tools/echel.py doctor
```

## Product-Facing Commands
- `build`: prepares an agent-ready implementation packet.
- `review`: creates a review report for implementation readiness.
- `next`: selects the next open task with graph context in mind.

## Generated Artifacts
- `wiki/reports/work-packets/{TASK-id}-packet.md`
- `wiki/reports/reviews/{TASK-id}-review.md`
- `wiki/reports/product-graph-report.md`

## Packet Expectations
Packets include product context, graph context, task objective, acceptance criteria, evidence obligations, verification commands, memory-update requirements, and agent instructions.

## Review Expectations
Review reports check acceptance criteria, Definition of Done, verification commands, graph integrity, and evidence references. They explain what is missing before a task can be closed.

## Verification
```bash
make verify-phase3
```
