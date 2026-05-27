---
type: task
status: done
---
# TASK-0014 - Define Product Graph Schema

## Objective
Define the canonical product graph shape for nodes, edges, manual links, generated storage, and integrity rules.

## Scope
- Define graph file ownership and storage.
- Document node, edge, relationship, and validation expectations.

## Out of Scope
- Runtime graph database integration.

## Implementation Steps
1. Add schema documentation.
2. Define supported node and edge types.
3. Document integrity rules.

## Context Links
- [[../reports/echel-v2-product-direction-review]]
- [[../../schema/product-graph.schema]]

## Acceptance Criteria
- [x] Product graph schema exists.
- [x] Node and edge fields are documented.
- [x] Integrity expectations are documented.

## Definition of Done
- Schema is available to agents and maintainers.

## Verification Commands
```bash
make wiki-health
```

## Documentation Updates
- Added `schema/product-graph.schema.md`.
