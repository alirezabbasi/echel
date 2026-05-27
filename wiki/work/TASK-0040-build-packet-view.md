---
type: task
status: done
---
# TASK-0040 - Build Packet View

## Context
- [[../../schema/work-packet.schema]]

## Objective
Let users inspect generated build packet artifacts from the cockpit.

## Scope
- List packet report files.
- Connect dashboard action to `build`.

## Out of Scope
- Rich markdown rendering.

## Implementation Steps
1. Expose packet files through snapshot.
2. Render packet list.
3. Add build command action.

## Acceptance Criteria
- [x] Packet view exists.
- [x] Build action is available from cockpit.

## Definition of Done
- Agent handoffs are visible in the cockpit.

## Verification Commands
```bash
make verify-phase4
```

## Documentation Updates
- Updated cockpit UI.

