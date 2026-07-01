# Where Are We

Last updated: 2026-07-02

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
- Completed Phase 2 product graph workflows through `graph`, `feature`, `risk`, and `link` commands.
- Completed Phase 3 graph-backed work packets and review reports through `build` and `review`.
- Completed Phase 4 product cockpit foundation over the wiki, graph, work, packets, reviews, risks, and decisions.
- Completed Phase 5 milestone readiness, proof packs, release summaries, and cockpit readiness.
- Completed V2 requirements hardening for initialization, commands, graph coverage, packets, cockpit, readiness, and framework-core boundaries.
- Added `docs/development/methodology.md` as the Echel vNext methodology contract for the full Product Discovery Specification to operations lifecycle.

## Next

1. Add lifecycle stage schema aligned with the vNext methodology contract.
2. Add traceability ID system for discovery, canon, requirements, domain, architecture, tasks, tests, evidence, release, and operations.
3. Add Product Discovery Specification templates and discovery quality gate.
4. Expand graph, readiness, cockpit, and prompts around lifecycle stages.
5. Expand release readiness into production operation and post-release learning loops.

## Risks/Blocks

- Contract drift across docs/schema/tools could weaken deterministic validation if not gated.
- Adding new folders without a unique purpose could reintroduce navigation complexity.
