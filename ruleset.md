# Echel Global Ruleset

This is the highest-priority instruction set for this scaffold.

## Rule 0: Scope and Precedence

- `ruleset.md` is the top-level project ruleset.
- `docs/ruleset.md` must remain aligned with this file and may add implementation detail.
- If there is a conflict, apply the stricter rule unless a documented ADR approves an exception.

## Rule 1: Knowledge Must Be Persistent

- Durable reasoning must not remain only in chat.
- Architecture, decisions, standards, and execution context must be captured in wiki artifacts.
- Update canonical wiki pages when concepts change.

## Rule 2: Session Resume Protocol Is Mandatory

At session start, load:

1. `ruleset.md`
2. `docs/ruleset.md`
3. `schema/*.md`
4. `wiki/index.md`
5. `wiki/project-brief.md`
6. `wiki/log.md` (recent entries)
7. `docs/development/state/where-are-we.md`
8. `docs/development/state/current-state.md`
9. `docs/development/work.md`

## Rule 3: Task Discipline

- Every task must follow the task template and include context links, acceptance criteria, definition of done, verification commands, and documentation update scope.
- No context link, no task.

## Rule 4: Quality Gates Are Required

- `make wiki-health` is mandatory before closure.
- Critical gate failures must be fixed or explicitly documented before completion.

## Rule 5: Governance and Traceability

- Major decisions require ADRs.
- Bugs must be recorded in `docs/development/bugs/BUG-*.md`.
- Debug commands must be logged in `docs/development/bugs/debug-commands.md`.

## Rule 6: Keep It General-Purpose

- Do not hardcode business-domain logic, taxonomy, or product-specific architecture into scaffold defaults.
- Domain specialization belongs in project-specific sources and derived wiki pages, not baseline templates.
