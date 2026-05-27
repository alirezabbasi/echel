---
type: task
status: done
---
# TASK-0019 - Add Graph-Aware Planning

## Objective
Ensure generated planning refreshes the graph report so work planning stays connected to product relationships.

## Scope
- Refresh graph report during synthesized planning.
- Print report path in planning output.

## Out of Scope
- Full automatic task prioritization from graph centrality.

## Implementation Steps
1. Build the graph report after plan synthesis.
2. Expose the graph report path to the operator.

## Context Links
- [[../roadmap]]
- [[../scope]]

## Acceptance Criteria
- [x] `echel plan` synthesizes MVP work.
- [x] `echel plan` writes a graph report.
- [x] Planning output points to the graph report.

## Definition of Done
- Planning leaves behind an updated graph report.

## Verification Commands
```bash
python3 tools/echel.py plan
```

## Documentation Updates
- Updated `tools/echel.py`.
