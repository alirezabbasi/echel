---
type: task
status: done
---
# TASK-0027 - Evidence Obligations Per Task

## Context
- [[../../schema/evidence.schema]]
- [[../../schema/work-packet.schema]]

## Objective
Connect generated packets to explicit evidence duties.

## Scope
- Add evidence obligation section to packets.
- Remind agents to register and link evidence before closure.

## Out of Scope
- Automatic evidence registry population.

## Implementation Steps
1. Derive obligations from task verification commands.
2. Add closure evidence guidance to packets.
3. Surface evidence gaps in review reports.

## Acceptance Criteria
- [x] Packets include `Evidence Obligations`.
- [x] Review reports show missing evidence references.

## Definition of Done
- Agent handoffs explain evidence expectations.

## Verification Commands
```bash
make verify-phase3
```

## Documentation Updates
- Updated Phase 3 guide.

