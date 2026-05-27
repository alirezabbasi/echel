---
type: task
status: done
---
# TASK-0023 - Graph-Backed Work Packet Context

## Context
- [[../reports/echel-v2-product-direction-review]]
- [[../reports/product-graph-report]]

## Objective
Upgrade work packets so agents receive related product graph context.

## Scope
- Include related requirements, users, needs, features, risks, decisions, and architecture nodes.
- Refresh graph reports during packet generation.

## Out of Scope
- LLM-generated semantic graph expansion.

## Implementation Steps
1. Build graph context from `wiki/graph.json`.
2. Add graph sections to work packets.
3. Verify generated packets in a scratch project.

## Acceptance Criteria
- [x] Work packets include `Graph Context`.
- [x] Packet generation refreshes graph reporting.

## Definition of Done
- Agents receive graph-backed context before implementation.

## Verification Commands
```bash
make verify-phase3
```

## Documentation Updates
- Updated `tools/echel/product.py`.

