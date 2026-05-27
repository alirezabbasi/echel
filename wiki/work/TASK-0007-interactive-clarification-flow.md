---
type: task
status: done
---
# TASK-0007 - Interactive Clarification Flow

## Context
- [[../project]]
- [[../reports/echel-v2-product-direction-review]]

## Objective
Allow product clarification answers to update product-owned wiki pages.

## Scope
- Add named clarification fields.
- Add `echel clarify --field <key> --answer <text>`.
- Sync key answers into product summaries.

## Out of Scope
- AI-generated follow-up questions.

## Implementation Steps
1. Define clarification field map.
2. Add answer write path.
3. Validate generated project behavior.

## Acceptance Criteria
- Clarification gaps list stable field keys.
- Answers update the correct wiki sections.

## Definition of Done
- Command works in generated `echel-core`.

## Verification Commands
```bash
make verify-phase1
```

## Documentation Updates
- Update Phase 1 user journey.
