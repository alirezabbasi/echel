# Development Operating System

This folder is the project execution control plane.

It owns repeatable SDLC procedure, execution controls, gates, evidence contracts, automation contracts, and active operating snapshots. Durable project meaning and relationship modeling belong in `wiki/`.

When a concept appears in both places, use this boundary:

- `wiki/`: what the project knows and how ideas relate.
- `docs/development/`: how the project is operated and verified.

## Structure

- `00-governance/`: operating policies and controls.
- `03-architecture/`: lifecycle architecture and system design contracts.
- `02-execution/`: active backlog and execution board.
- `05-automation/`: workflow, CLI, and orchestration specifications.
- `06-evidence/`: artifact registry and proof model specifications.
- `04-memory/`: persistent memory snapshots and decision trace.
- `debugging/`: bug registry and command logs.

## Mandatory resume read order

1. `ruleset.md`
2. `docs/ruleset.md`
3. `schema/*.md`
4. `wiki/index.md`
5. `wiki/project-brief.md`
6. `wiki/log.md` (recent entries)
7. `docs/development/04-memory/WHERE_ARE_WE.md`
8. `docs/development/04-memory/CURRENT_STATE.md`
9. `docs/development/02-execution/KANBAN.md`
