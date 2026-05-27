---
type: task
status: done
---
# TASK-0016 - Extract Graph From Wiki

## Objective
Generate product graph nodes and edges from product pages, work items, decisions, risks, and architecture.

## Scope
- Extract nodes from product wiki pages and work artifacts.
- Generate deterministic product relationships.
- Merge human-curated manual relationships.

## Out of Scope
- Semantic embedding or LLM-based graph extraction.

## Implementation Steps
1. Parse product page sections.
2. Convert sections and artifacts into graph nodes.
3. Add deterministic edges.
4. Include manual graph edges.

## Context Links
- [[../problem]]
- [[../users]]
- [[../solution]]
- [[../scope]]
- [[../architecture]]

## Acceptance Criteria
- [x] Product, problem, user, need, solution, feature, requirement, component, task, decision, and risk nodes can be extracted.
- [x] Deterministic relationships are generated from wiki structure.
- [x] Manual relationships can be merged.

## Definition of Done
- `echel graph show` can summarize extracted relationships.

## Verification Commands
```bash
python3 tools/echel.py graph show
```

## Documentation Updates
- Added graph extraction behavior in `tools/echel/graph.py`.
