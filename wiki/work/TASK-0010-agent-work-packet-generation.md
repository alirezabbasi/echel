---
type: task
status: done
---
# TASK-0010 - Agent Work Packet Generation

## Context
- [[../project]]
- [[../knowledge/ai-native-engineering-os]]

## Objective
Generate agent-ready work packets from the next open product task.

## Scope
- Add `echel packet`.
- Include product context, task objective, acceptance criteria, constraints, verification, and memory updates.

## Out of Scope
- Model-specific prompt rendering.

## Implementation Steps
1. Select next open task.
2. Compose work packet report.
3. Append log entry.

## Acceptance Criteria
- Work packet is written under `wiki/reports/work-packets/`.

## Definition of Done
- Packet generation works in generated projects.

## Verification Commands
```bash
make verify-phase1
```

## Documentation Updates
- Update Phase 1 guide.
