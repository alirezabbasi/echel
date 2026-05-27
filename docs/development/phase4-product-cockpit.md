---
type: guide
status: active
---
# Phase 4 Product Cockpit

Phase 4 turns Echel's product memory, graph, packets, reviews, risks, decisions, and safe actions into a local cockpit.

## Core Surfaces
- Dashboard
- Clarification queue
- Roadmap
- Work queue
- Graph explorer
- Build packets
- Review reports
- Risks
- Decisions
- Chat

## Data Flow
The cockpit reads product state from `wiki/`, graph state from `wiki/graph.json`, generated reports from `wiki/reports/`, and safe command output from `tools/echel.py`.

## Safe Actions
- `clarify`
- `plan`
- `build`
- `review`
- `graph-report`
- `status`
- `next`

## Verification
```bash
make verify-phase4
```
