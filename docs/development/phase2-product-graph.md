---
type: guide
status: active
---
# Phase 2 Product Graph

Phase 2 turns the product wiki into a typed relationship graph. The graph helps Echel reason about how product intent, users, needs, requirements, features, architecture, risks, decisions, and work items relate to each other.

## Responsibility Boundary
The graph belongs to the target product because it is generated from product memory. In initialized projects, it lives in the root `wiki/` next to the rest of the product intelligence.

The graph tools belong to Echel Core because they define the method used to extract, validate, and report product relationships.

## Generated Artifacts
- `wiki/graph.json`: machine-readable graph.
- `wiki/graph.manual.json`: optional human-curated relationships.
- `wiki/reports/product-graph-report.md`: readable graph coverage and integrity report.

## Command Flow
```bash
python3 tools/echel.py feature add --title "Product memory graph" --summary "Typed product relationship map."
python3 tools/echel.py risk add --title "Ambiguous requirements" --impact "Misaligned implementation." --mitigation "Validate work through the graph."
python3 tools/echel.py graph build
python3 tools/echel.py graph validate
python3 tools/echel.py graph report
python3 tools/echel.py status
```

## Planning Flow
`echel plan` now refreshes the product graph report after synthesizing the MVP plan. This keeps generated work tied to visible product relationships instead of isolated task text.

## Validation Expectations
- Product intent exists.
- Problem, users, solution, MVP requirements, and tasks are represented.
- Tasks are linked to requirements.
- Risks include mitigation.
- Generated reports are committed as durable product memory.
