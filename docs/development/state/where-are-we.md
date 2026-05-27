# Where Are We

Last updated: 2026-05-27

## Completed

- Established Echel as a general-purpose LLM engineering scaffold.
- Added governance, execution, and memory control documents.
- Added the project intelligence compounding model as a canonical system artifact.
- Defined the four-layer OS model with v1 architecture/contracts for Execution, Evidence, and Automation layers.

## Recent

- Expanded the development loop to include bug management and RCA.
- Added an operational methodology doc for disciplined loop execution.
- Added Claude Code and Cursor prompt packs alongside Codex prompts.
- Added deterministic gate runner contract and evidence/proof-pack specifications.
- Clarified Echel as a domain-expert-guided AI-native development platform and documented the wiki/development-doc ownership boundary.
- Simplified the visible folder structure around human-readable purposes.
- Updated generated project topology so `wiki/` belongs to the product root and `docs/development/` stays inside `echel-core/`.

## Current

- Running v2 MVP foundation commands with declarative project contract loading.
- Enforcing integrity through `echel doctor` drift and evidence/gate reporting.
- Using `wiki/knowledge`, `wiki/decisions`, `wiki/work`, and `wiki/reports` as the project memory model.
- Using `WIKI_ROOT` so Echel can operate from `echel-core/` while maintaining root-level product memory.
- Completed Phase 1 deterministic product-owner workflows through `define`, `clarify`, `plan`, `status`, `next`, and `packet`.

## Next

1. Add durable memory kernel and contradiction tracking.
2. Add differential conformance tooling and CI summary outputs.
3. Add migration planner, runtime adapters, and safety rails.
4. Continue reducing duplicated documentation content inside the simplified structure.

## Risks/Blocks

- Contract drift across docs/schema/tools could weaken deterministic validation if not gated.
- Adding new folders without a unique purpose could reintroduce navigation complexity.
