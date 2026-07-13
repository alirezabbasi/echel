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

## Guided Stage Actions

Every lifecycle stage exposes command-backed guided actions. Some actions run immediately, and some render a small form for required command inputs.

Examples:
- Discovery can list gaps, answer a discovery field, or run the discovery gate.
- Canon can generate canon files or check canon drift.
- Strategy can evaluate readiness or generate strategy artifacts.
- Requirements, Domain, and Architecture can generate their lifecycle artifacts and run their stage gates.
- Roadmap and Execution can create plans, execution tasks, next-task guidance, and work packets.
- Build can generate build or review packets.
- Validate can run validation summaries and register evidence.
- Release can run release readiness, proof packs, and release summaries.
- Operate can inspect or record learning.
- Governance can regenerate graph, traceability, repository integrity, contradiction-register, and migration-compatibility reports.

## Data Flow
The cockpit reads product state from `wiki/`, graph state from `wiki/graph.json`, generated reports from `wiki/reports/`, lifecycle gates from `tools/echel/gates.py`, readiness state from `tools/echel/readiness.py`, and safe command output from `tools/echel.py`.

## Safe Actions
- `clarify`
- `discover`
- `canon`
- `canon-drift`
- `strategy`
- `strategy-readiness`
- `requirements`
- `domain`
- `architecture`
- `execution-tasks`
- `repository-factory`
- `plan`
- `packet`
- `build`
- `review`
- `graph-report`
- `traceability`
- `integrity-audit`
- `contradictions-sync`
- `migration-compatibility`
- `validate`
- `evidence-add`
- `learning`
- `learning-add`
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
