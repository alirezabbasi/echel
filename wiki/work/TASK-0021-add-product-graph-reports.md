---
type: task
status: done
---
# TASK-0021 - Add Product Graph Reports

## Objective
Generate readable product graph reports for product owners and AI agents.

## Scope
- Generate graph coverage summaries.
- Generate graph integrity summaries.
- Store reports under `wiki/reports/`.

## Out of Scope
- Browser-based graph visualization.

## Implementation Steps
1. Add report writer.
2. Include summary, issues, and coverage.
3. Refresh generated graph when writing the report.

## Context Links
- [[../reports/echel-v2-product-direction-review]]

## Acceptance Criteria
- [x] Product graph report command exists.
- [x] Report includes node counts, edge counts, issue counts, and coverage.
- [x] Report is stored in `wiki/reports/`.

## Definition of Done
- `echel graph report` writes a readable report.

## Verification Commands
```bash
python3 tools/echel.py graph report
```

## Documentation Updates
- Added `wiki/reports/product-graph-report.md` generation behavior.
