---
type: task
status: done
---
# TASK-0031 - Agent Memory Update Checklist

## Context
- [[../log]]
- [[../../schema/work-packet.schema]]

## Objective
Ensure packets tell agents which memory surfaces must be updated after work.

## Scope
- Include task, product page, graph relationship, report, and log updates.

## Out of Scope
- Automatically editing every affected product page.

## Implementation Steps
1. Expand packet memory update section.
2. Include graph refresh expectations.
3. Verify packet content.

## Acceptance Criteria
- [x] Packets include required memory update instructions.
- [x] Graph relationship changes are called out.

## Definition of Done
- Agents know how to preserve continuity after implementation.

## Verification Commands
```bash
make verify-phase3
```

## Documentation Updates
- Updated Phase 3 guide.

