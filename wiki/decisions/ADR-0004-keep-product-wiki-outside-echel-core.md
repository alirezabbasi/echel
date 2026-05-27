---
type: adr
status: accepted
---
# ADR-0004 — Keep Product Wiki Outside Echel Core

## Decision
Generated projects keep `wiki/` at the target project repository root and place framework machinery inside `echel-core/`.

`echel-core/project.echel` points `WIKI_ROOT` to `../wiki` so Echel tools can run from `echel-core/` while reading and writing product-owned memory.

## Consequences
- `wiki/` is part of the product repository and should be committed with the project.
- `docs/development/` remains inside `echel-core/` because it defines Echel's SDLC method, workflows, operational controls, and framework state.
- Generated project roots stay less cluttered because framework files, schemas, prompts, tools, and development methodology live under `echel-core/`.
- Tools must resolve wiki paths through `WIKI_ROOT` rather than assuming the wiki is inside the current working directory.
