---
type: task
status: done
---
# TASK-0008 - Product-First Wiki Template Cleanup

## Context
- [[../project]]
- [[../decisions/ADR-0004-keep-product-wiki-outside-echel-core]]

## Objective
Ensure generated projects start with product memory rather than Echel framework memory.

## Scope
- Generate minimal root `wiki/`.
- Keep framework docs and knowledge under `echel-core`.
- Reset generated core work board.

## Out of Scope
- Removing framework knowledge from this Echel development repo.

## Implementation Steps
1. Replace full wiki copy with minimal product wiki generation.
2. Keep `WIKI_ROOT=../wiki`.
3. Verify generated health checks.

## Acceptance Criteria
- Generated root wiki contains product pages and purpose folders.
- Generated core work board has no scaffold tasks.

## Definition of Done
- Generated project gates pass.

## Verification Commands
```bash
make verify-phase1
```

## Documentation Updates
- Update initialization docs.
