---
type: guide
status: active
---
# Phase 4 Product Cockpit

Phase 4 turns Echel's product memory, graph, packets, reviews, risks, decisions, lifecycle gates, AI roles, and safe actions into a local cockpit.

## Core Surfaces

The primary navigation is the lifecycle flow:

- Discovery
- Canon
- Strategy
- Requirements
- Domain
- Architecture
- Roadmap
- Execution
- Build
- Validate
- Release
- Operate
- Governance
- Chat

Artifact views remain available as stage context inside the lifecycle views. For example, Discovery embeds the clarification queue, Architecture embeds the architecture map, Execution embeds the work queue, Build embeds packet reports, Validate embeds review reports, and Governance embeds graph, contradiction, and decision context.

## Always-Visible Steering State

The cockpit header and stage detail always show:

- current lifecycle stage
- stage blockers
- next action
- responsible AI role

This makes the cockpit a steering interface for the Echel lifecycle instead of a passive dashboard over documentation files.

## Data Flow
The cockpit reads product state from `wiki/`, graph state from `wiki/graph.json`, generated reports from `wiki/reports/`, lifecycle gates from `tools/echel/gates.py`, readiness state from `tools/echel/readiness.py`, and safe command output from `tools/echel.py`.

## Safe Actions
- `clarify`
- `plan`
- `build`
- `review`
- `graph-report`
- `readiness`
- `proof-pack`
- `release-summary`
- `status`
- `next`

Stage safe actions are intentionally command-backed. They do not create an independent cockpit source of truth.

## Verification
```bash
make verify-phase4
```
