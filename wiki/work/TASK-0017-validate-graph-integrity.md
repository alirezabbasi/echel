---
type: task
status: done
---
# TASK-0017 - Validate Graph Integrity

## Objective
Validate graph coverage, dangling relationships, duplicate node ids, task-to-requirement coverage, and risk mitigation.

## Scope
- Report missing required product concepts.
- Report broken graph references.
- Report uncovered tasks and unmitigated risks.

## Out of Scope
- Blocking all major issues during early discovery.

## Implementation Steps
1. Add graph issue model.
2. Validate node and edge integrity.
3. Surface issues through the CLI.

## Context Links
- [[../reports/echel-v2-product-direction-review]]
- [[../../schema/product-graph.schema]]

## Acceptance Criteria
- [x] Graph validation command exists.
- [x] Critical and major graph issues are reported.
- [x] Validation can run in generated projects.

## Definition of Done
- `echel graph validate` reports actionable graph issues.

## Verification Commands
```bash
python3 tools/echel.py graph validate
```

## Documentation Updates
- Added validation rules in `tools/echel/graph.py`.
