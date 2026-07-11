# Where Are We

Last updated: 2026-07-11

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
- Added `schema/lifecycle-stage.schema.md` as the deterministic lifecycle stage contract for future stage gates and tooling.
- Added traceability, discovery, canon, strategy, and requirements model artifacts needed to preserve product intent from idea through execution planning.
- Re-approved TASK-0003 through TASK-0011 after tightening gates, canon drift handling, template promotion safeguards, and canon-driven strategy generation.
- Added the requirements command layer that turns canon and strategy into generated requirement rows and graph nodes without replacing hand-authored requirement context.
- Added the requirements readiness gate so `echel readiness --stage requirements` can block domain and architecture work until MVP requirements are testable, accepted, risk-aware, dependency-aware, scoped, and covered by NFRs.
- Added first-class domain model templates under `wiki/domain/`, including a complete current requirement-to-domain coverage map and technology-neutral domain guardrails.
- Added the domain command layer that turns requirement rows into generated domain concepts, contexts, aggregates, events, workflows, rules, and graph nodes without replacing authored domain guidance.
- Added the domain consistency gate so `echel readiness --stage domain` can block architecture until requirement coverage, domain ID integrity, graph coverage, duplicate-meaning checks, and technology-neutral language pass.
- Added the expanded architecture artifact model under `wiki/architecture/` so architecture can preserve domain boundaries, carry rationale, and prepare for generation and readiness gates.
- Added the architecture command layer that turns gated domain coverage into generated architecture rows and graph nodes without replacing authored architecture guidance.
- Added the architecture readiness gate so `echel readiness --stage architecture` can block roadmap work until deployment posture, data/security/observability models, ADR coverage, requirement/domain mappings, graph coverage, and complexity risk pass.
- Added the roadmap artifact expansion so `wiki/roadmap/` now contains master, MVP, architecture, engineering, and release roadmaps with phase objectives, scope, dependencies, demos, risks, and exit gates.
- Added execution phase artifacts under `wiki/execution/` so foundation, MVP, hardening, production, and evolution phases have task lists, dependencies, DoD, validation methods, documentation obligations, and expected repo changes.
- Added the execution task generator so `python3 tools/echel.py execution-tasks` creates 20 agent-executable `wiki/work/TASK-1xxx-*.md` records and `wiki/work/TASK_INDEX.md` from the phase artifacts.
- Added the repository factory generator so `python3 tools/echel.py repository-factory` creates `generated/product-repository/` with app/config/test/CI/env/local-doc baseline and a repository factory report.
- Added `wiki/engineering/` as the product-owned engineering contract and made generated setup, start, syntax-lint, test, CI, and verification commands exact and reproducible.
- Added the vNext AI-agent role model in `wiki/agents/role-model.md` and `docs/development/methodology.md`: all 13 roles (Founder Interviewer through Governance Auditor) now define responsibilities, inputs, outputs, and forbidden actions, with a lifecycle-stage mapping and a shared binding to `wiki/engineering/development-workflow.md`.
- Added canonical lifecycle playbooks under `prompts/playbooks/` and tool render maps for Codex, Claude Code, and Cursor so tool-specific prompts derive from one guarded lifecycle prompt source.

## Next

1. Add agent handoff rules.
2. Expand graph, readiness, cockpit, and prompts around lifecycle stages.
3. Expand release readiness into production operation and post-release learning loops.

## Risks/Blocks

- Contract drift across docs/schema/tools could weaken deterministic validation if not gated.
- Adding new folders without a unique purpose could reintroduce navigation complexity.
- Template-derived content must not be promoted into canon or strategy as product truth.
- Requirements command graph integration currently uses manual graph nodes until the broader traceability graph upgrade lands.
