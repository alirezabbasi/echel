---
type: task
status: done
---
# TASK-0052 - Evidence Coverage Validation

## Context
- [[../../schema/evidence.schema]]

## Objective
Validate that completed readiness-bound tasks have registered evidence.

## Scope
- Check done task evidence IDs.
- Check evidence registry membership.
- Report blockers for missing evidence.

## Out of Scope
- Automatic evidence creation.

## Implementation Steps
1. Read task evidence links.
2. Compare with evidence registry.
3. Add readiness blockers for missing coverage.

## Acceptance Criteria
- [x] Done tasks without registered evidence block readiness.
- [x] Proof packs summarize evidence registry count.

## Definition of Done
- Readiness cannot silently pass without evidence.

## Verification Commands
```bash
make verify-phase5
```

## Documentation Updates
- Updated Phase 5 guide.

