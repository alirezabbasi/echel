# Echel Governance Ruleset

This file extends `ruleset.md` with operational controls.

## Documentation and Memory Controls

- Keep `wiki/index.md` and `wiki/log.md` current.
- Maintain memory artifacts:
  - `docs/development/state/current-state.md`
  - `docs/development/state/session-ledger.md`
  - `docs/development/state/decision-log.md`
  - `docs/development/state/risks-and-assumptions.md`

## Execution Controls

- Execution tracking lives in `docs/development/work.md`.
- Task statuses must match evidence in wiki and development memory docs.
- Non-completed tasks require explicit Definition of Done.

## Debugging Controls

- Register every discovered bug in `docs/development/bugs/BUG-00001.md` style.
- Log development/debug commands in `docs/development/bugs/debug-commands.md` with timestamp, command, purpose, and status.

## Status Protocol

`wrw` is the dedicated "Where Are We?" shortcut command for rapid status.

When asked "Where are we?" (or when running `make wrw`), answer with exactly:

- Completed
- Recent
- Current
- Next
- Risks/Blocks

Source that answer from current state, session ledger, and kanban documents.
Keep `docs/development/state/where-are-we.md` synchronized as the concise snapshot artifact for this protocol.
