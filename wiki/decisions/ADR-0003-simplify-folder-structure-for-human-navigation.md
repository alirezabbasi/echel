---
type: adr
status: accepted
---
# ADR-0003 — Simplify Folder Structure for Human Navigation

## Decision
Use fewer, purpose-named folders for Echel's visible project memory and development controls.

The canonical structure is:

- `wiki/knowledge`: concepts, systems, entities, flows, and standards
- `wiki/decisions`: durable ADRs
- `wiki/work`: task artifacts
- `wiki/reports`: analysis, generated checks, and source summaries
- `docs/development`: operating files for method, work, architecture, governance, automation, and evidence
- `docs/development/state`: current state, resume snapshots, session history, decision log, and risks
- `docs/development/bugs`: bug records and debugging evidence

## Consequences
Folder names should explain their purpose to non-technical project owners without requiring knowledge of internal SDLC taxonomy.

New folders require a distinct user-facing purpose. Otherwise, new material should be added to an existing folder or consolidated into a clearer file.
