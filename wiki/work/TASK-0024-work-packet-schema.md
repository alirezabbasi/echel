---
type: task
status: done
---
# TASK-0024 - Work Packet Schema

## Context
- [[../../schema/work-packet.schema]]

## Objective
Define the canonical structure for agent work packets.

## Scope
- Document required packet sections.
- Document producer commands and review relationship.

## Out of Scope
- JSON serialization of packets.

## Implementation Steps
1. Add schema documentation.
2. Align generated packet sections with the schema.

## Acceptance Criteria
- [x] Work packet schema exists.
- [x] Generated packets include required sections.

## Definition of Done
- Packet shape is documented for agents and maintainers.

## Verification Commands
```bash
make wiki-health
```

## Documentation Updates
- Added `schema/work-packet.schema.md`.

