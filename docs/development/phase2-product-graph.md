---
type: guide
status: active
---
# Phase 2 Product Graph

Phase 2 turns the product wiki into a typed relationship graph. The graph helps Echel reason about how product intent, users, needs, requirements, features, architecture, risks, decisions, and work items relate to each other.

The vNext graph now also includes lifecycle coverage nodes so AI agents can traverse the methodology from discovery through strategy, requirements, domain, architecture, validation, deployment, operations, contradiction handling, and learning. This keeps Echel aligned with the engineering OS model rather than treating the graph as a narrow product backlog map.

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

## Lifecycle Coverage
- Discovery: `discovery-item`, `assumption`, `hypothesis`, `buyer`, and `stakeholder`.
- Strategy and requirements: `strategy` and `requirement`.
- Domain and architecture: `domain-concept`, `bounded-context`, `business-rule`, `architecture`, and `architecture-component`.
- Execution and verification: `task`, `test`, and `evidence`.
- Release and operation: `deployment-artifact`, `operation-artifact`, `milestone`, and `release`; operation artifacts include `wiki/operations/*.md` support, incident, recovery, SLO, change, and evolution records.
- Governance and evolution: `contradiction`, `learning`, `decision`, and `risk`.

## Metadata Discipline
Every generated graph node carries `statement_type`, `confidence`, `source_stage`, and `verification_status`. Nodes also carry `trace_id` when a stable methodology ID can be inferred from the node ID or structured source row.

When source artifacts do not declare confidence, the graph records `unknown` instead of inventing certainty. A low-confidence assumption that remains unverified, unaccepted, or unresolved is a critical graph validation issue because later stages must not treat it as safe product truth.
