---
type: operations-learning-loop
stage: operations-evolution
status: draft
owner: operations-steward
updated: 2026-07-13
---
# Learning Loop

## Purpose

The learning loop turns post-release signals into governed product memory updates. It prevents incidents, RCA, customer feedback, roadmap changes, and strategy changes from staying in chat or local memory only.

## Command Contract

Use:

```bash
python3 tools/echel.py learning add --source-kind incident --title "..." --summary "..." --action task
```

Allowed source kinds: `incident`, `rca`, `feedback`, `roadmap-change`, `strategy-change`.

Allowed actions: `task`, `adr`, `risk`, `assumption`, `strategy-change`, `none`.

## Learning Flow

| ID | Step | Action | Output | Owner |
| --- | --- | --- | --- | --- |
| LRN-FLOW-001 | Capture | Record the signal with source kind, title, summary, owner, and severity. | [[learning-records]] | Operations Steward |
| LRN-FLOW-002 | Classify | Choose whether it creates task, ADR, risk, assumption, strategy change, or no-op. | Learning record action | Governance Auditor |
| LRN-FLOW-003 | Route | Update the authoritative artifact for the chosen action. | Work, decisions, risks, assumptions, or strategy memory | Responsible role |
| LRN-FLOW-004 | Verify | Run validation and register evidence when behavior changes. | Evidence record | QA Agent |
| LRN-FLOW-005 | Close | Update evolution backlog and learning record status. | [[evolution-backlog]] | Operations Steward |

## Quality Gate

- [ ] Learning records have source kind, owner, severity, action, and target artifact.
- [ ] Product behavior changes route through task packets.
- [ ] Architecture decisions route through ADRs.
- [ ] Risks, assumptions, roadmap changes, and strategy changes update their authoritative memory surfaces.
