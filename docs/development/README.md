# Development Operating System

This folder is the project execution control plane.

It owns repeatable SDLC procedure, execution controls, gates, evidence contracts, automation contracts, and active operating snapshots. Durable project meaning and relationship modeling belong in `wiki/`.

In generated projects, this folder lives under `echel-core/docs/development/`. The target product's `wiki/` lives at the project repository root and is resolved through `WIKI_ROOT`.

When a concept appears in both places, use this boundary:

- `wiki/`: what the project knows and how ideas relate.
- `docs/development/`: how the project is operated and verified.

## Structure

- `method.md`: how ideas become verified work.
- `work.md`: the active backlog and execution board.
- `architecture.md`: Echel's system shape and lifecycle model.
- `governance.md`: delivery controls and gate rules.
- `automation.md`: CLI and workflow automation contracts.
- `evidence.md`: proof and artifact registry rules.
- `state/`: current state, session history, decisions, risks, and resume snapshots.
- `bugs/`: bug records and debugging command evidence.

## Mandatory resume read order

1. `ruleset.md`
2. `docs/ruleset.md`
3. `schema/*.md`
4. `wiki/index.md`
5. `wiki/project-brief.md`
6. `wiki/log.md` (recent entries)
7. `docs/development/state/where-are-we.md`
8. `docs/development/state/current-state.md`
9. `docs/development/work.md`
