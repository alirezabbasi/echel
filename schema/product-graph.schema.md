---
type: schema
status: active
---
# Product Graph Schema

The product graph is the machine-readable relationship layer for Echel product memory. It is generated from the product-owned `wiki/` and stored at `wiki/graph.json`.

## File
- Path: `wiki/graph.json`
- Owner: target product repository
- Producer: `python3 tools/echel.py graph build`
- Report: `wiki/reports/product-graph-report.md`

## Graph
```json
{
  "version": 1,
  "generated_at": "2026-05-27T00:00:00Z",
  "nodes": [],
  "edges": []
}
```

## Node
```json
{
  "id": "feature:product-memory-graph",
  "type": "feature",
  "title": "Product memory graph",
  "source": "solution.md",
  "summary": "Product memory graph",
  "trace_id": "",
  "statement_type": "decision",
  "confidence": "unknown",
  "source_stage": "product-memory",
  "verification_status": "unverified"
}
```

Required fields:
- `id`: stable identifier in `{type}:{slug}` form.
- `type`: product concept type.
- `title`: human-readable name.
- `source`: wiki-relative source artifact.
- `summary`: short source-derived explanation.
- `trace_id`: stable methodology ID when one is available, otherwise empty.
- `statement_type`: one of `fact`, `observation`, `assumption`, `hypothesis`, `decision`, `constraint`, `risk`, or `question`.
- `confidence`: one of `high`, `medium`, `low`, or `unknown` when source artifacts do not yet declare confidence.
- `source_stage`: lifecycle stage where the node originated or is primarily maintained.
- `verification_status`: one of `unverified`, `active`, `draft`, `generated`, `verified`, `accepted`, `resolved`, or `done`.

Core node types:
- `product`
- `problem`
- `user`
- `need`
- `solution`
- `feature`
- `requirement`
- `workflow`
- `component`
- `task`
- `evidence`
- `decision`
- `risk`
- `milestone`
- `release`

Lifecycle node types:
- `discovery-item`
- `assumption`
- `hypothesis`
- `buyer`
- `stakeholder`
- `strategy`
- `business-rule`
- `domain-concept`
- `bounded-context`
- `architecture`
- `architecture-component`
- `test`
- `deployment-artifact`
- `operation-artifact`
- `governance-artifact`
- `contradiction`
- `learning`

The lifecycle node types make the graph represent the full methodology path rather than only the early product/task memory model. They may be extracted from structured rows when stable methodology IDs exist, or from lifecycle artifact registers when a stage exists but the product has not yet captured non-template rows.

## Edge
```json
{
  "from_id": "feature:product-memory-graph",
  "to_id": "requirement:product-graph",
  "type": "implements"
}
```

Required fields:
- `from_id`: existing source node id.
- `to_id`: existing target node id.
- `type`: relationship label.

Common edge types:
- `defines`
- `addressed_by`
- `serves`
- `has_need`
- `satisfies`
- `includes`
- `implements`
- `supports`
- `enables`
- `requires`
- `planned_as`
- `delivers`
- `has_evidence`
- `verifies`
- `constrained_by`
- `has_risk`
- `tracks`
- `depends_on`
- `related_to`
- `has_lifecycle_artifact`
- `informs`
- `refines`
- `constrains`
- `realized_by`
- `runs`
- `operates`
- `feeds`

## Manual Relationships
Manual relationships are stored in `wiki/graph.manual.json` and merged during graph build. Manual edges should be used only when the relationship cannot be deterministically inferred from current wiki structure.

## Integrity Rules
- Every graph must contain product, problem, user, solution, requirement, and task coverage before it is considered ready for execution.
- Every edge must reference existing node ids.
- Every task should connect to at least one requirement.
- Every risk should include mitigation.
- Critical issues block graph integrity. Major issues indicate product memory is incomplete.
