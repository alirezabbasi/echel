---
type: task
status: done
---
# TASK-0043 - Cockpit Command Bridge

## Context
- [[../../schema/cockpit-api.schema]]

## Objective
Wire cockpit actions to safe Echel commands.

## Scope
- Clarify.
- Plan.
- Build.
- Review.
- Graph report.
- Status.
- Next.

## Out of Scope
- Arbitrary shell execution.

## Implementation Steps
1. Define safe action allowlist.
2. Add command endpoint.
3. Route UI actions through the endpoint.

## Acceptance Criteria
- [x] Command bridge blocks unknown actions.
- [x] Safe actions run through Echel CLI.

## Definition of Done
- Cockpit can steer product workflows without unsafe command exposure.

## Verification Commands
```bash
make verify-phase4
```

## Documentation Updates
- Added cockpit API schema.

