# Current State

Last updated: 2026-07-02

## Completed

- Established Echel as a general-purpose LLM engineering scaffold.

## Recent

- Added governance, execution, and memory control documents.
- Defined a project intelligence compounding model with delivery, reliability, and strategy loops.
- Added v1 Four-Layer OS architecture and contracts for Execution OS, Evidence OS, and Automation OS.
- Started Phase 3 implementation with memory kernel, conformance runner, migration planner, behavior contracts, runtime adapters, and workspace safety rails.
- Clarified Echel's product framing as a domain-expert-guided AI-native software development platform with persistent memory to overcome AI context limitations.
- Simplified the folder model around human-readable purposes: knowledge, decisions, work, reports, state, and bugs.
- Updated initialization so generated projects keep `wiki/` at the product root and framework methodology/tooling under `echel-core/`.

## Current

- Operating a v2 MVP CLI foundation with declarative project contracts, path abstraction, drift detection, evidence validation, and gate compilation.
- Hardening task closure and memory synchronization workflows through `echel` core commands.
- Building Platform MVP Sprint 1 for self-hosted multi-provider chat interface and Echel command orchestration via web runtime.
- Using the simplified folder model as the baseline for future Echel navigation and generated projects.
- Resolving product memory paths through `WIKI_ROOT`.
- Starting V2 Phase 1 with product-first initialization and product-owner commands.
- Completed deterministic Phase 1 command loop: clarify answers, MVP planning synthesis, work packets, readiness status, and generated-project verification.
- Completed Phase 2 product graph foundation: graph extraction, storage, validation, reports, graph-aware status/planning, relationship commands, and generated-project verification.
- Completed Phase 3 graph-backed agent work packets, product-facing build command, review reports, evidence obligations, graph-aware next-task selection, and generated-project verification.
- Completed Phase 4 product cockpit foundation: cockpit data API, dashboard, clarification, roadmap, work, graph, packet, review, risk, decision, chat views, safe command bridge, and generated-project verification.
- Completed Phase 5 milestone and release readiness: milestone command, readiness reports, proof packs, evidence/risk/review gates, release summaries, cockpit readiness view, and generated-project verification.
- Hardened V2 coverage against the requested product-first initialization, product-owner command language, graph, packet, cockpit, readiness, and framework-core boundaries.
- Added the Echel vNext methodology contract as the canonical lifecycle rule set for turning raw product ideas into production-ready repositories.
- Added `schema/lifecycle-stage.schema.md` to define deterministic vNext stage IDs, required artifacts, gate conditions, transitions, and blocking rules.
- Added the vNext traceability schema, discovery templates and command, discovery gate, canon templates and commands, strategy templates and commands, and requirements model templates.
- Re-reviewed TASK-0003 through TASK-0011 and remediated lifecycle drift: discovery gate coverage is stricter, canon generation rejects template-only source content, canon drift writes durable artifacts and stale markers, and strategy generation now reads from canon while preserving discovery references.
- Added `echel requirements` command to initialize, inspect, and generate requirement artifacts from canon and strategy while rejecting vague sources and adding requirement nodes to the product graph.
- Added `GATE-REQUIREMENTS` to evaluate requirement readiness before domain modeling by checking MVP testability, acceptance criteria, dependencies, risks, explicit out-of-scope records, MVP NFR coverage, and generated requirement graph links.
- Added `wiki/domain/` templates for domain overview, ubiquitous language, bounded contexts, entities, aggregates, domain events, workflows, and policies/rules with requirement-to-domain coverage.
- Added `echel domain` command to generate domain mappings from requirements, refresh domain generated sections, and add requirement/domain nodes to the product graph.
- Added `GATE-DOMAIN` to block architecture when domain artifacts have unmapped requirements, undefined domain IDs, duplicate meanings, missing generated graph nodes, or concrete technology leakage.
- Added the expanded architecture artifact model under `wiki/architecture/` with overview, context map, component, data, API, event, workflow, security, and observability architecture documents.

## Next

1. Add `echel architecture` to generate architecture from the gated domain model and requirements.
2. Add architecture readiness once architecture artifacts are modeled.
3. Implement lifecycle stage evaluation against `schema/lifecycle-stage.schema.md`.
4. Expand product graph and readiness gates to evaluate full methodology stages.
5. Replace duplicated tool prompts with canonical lifecycle playbooks.

## Risks/Blocks

- If execution/evidence schemas are adopted inconsistently, gate determinism will degrade.
- If new folders are added without a unique purpose, Echel may become harder for domain experts to navigate again.
- Force-generating from incomplete discovery remains risky; gates should keep treating template `TBD` content as incomplete.
- Requirements generation remains blocked until strategy is meaningful unless explicitly forced; the requirements gate now verifies the resulting artifacts before downstream domain work.
