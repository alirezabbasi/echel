# Current State

Last updated: 2026-07-12

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
- Added `echel architecture` to generate architecture mappings from gated domain coverage, refresh generated architecture sections, preserve the compatibility architecture summary, and add architecture nodes to the product graph.
- Added `GATE-ARCHITECTURE` to block roadmap work when architecture lacks deployment posture, data/security/observability models, ADR coverage, generated requirement/domain mappings, graph coverage, or justified complexity.
- Added the expanded roadmap artifact model under `wiki/roadmap/` with master, MVP, architecture, engineering, and release roadmap documents that turn gated architecture into phased delivery planning.
- Added explicit execution phase artifacts under `wiki/execution/` for foundation, MVP, hardening, production, and evolution phases with task lists, dependencies, DoD, validation methods, and expected repo changes.
- Added `echel execution-tasks` to turn execution phase rows into gated, agent-executable `wiki/work/TASK-1xxx-*.md` tasks plus `wiki/work/TASK_INDEX.md`.
- Added `echel repository-factory` to generate a local baseline under `generated/product-repository/` with app, config, tests, CI, env example, verification script, generated engineering docs, and a repository-factory report.
- Added `wiki/engineering/` as the product-owned engineering contract and made generated setup, start, syntax-lint, test, CI, and verification commands exact and reproducible.
- Added the vNext AI-agent role model in `wiki/agents/role-model.md` and `docs/development/methodology.md`: the 13-role virtual delivery team (Founder Interviewer through Governance Auditor) now defines responsibilities, inputs, outputs, and forbidden actions per role and a lifecycle-stage mapping, with every role bound to the shared `wiki/engineering/development-workflow.md` contract.
- Added canonical lifecycle playbooks under `prompts/playbooks/` and tool render maps for Codex, Claude Code, and Cursor so prompt packs render from one source while preserving the no-code-before-task-packet rule.
- Added `wiki/agents/handoff-protocol.md` as the required inter-role handoff contract and updated every canonical playbook to require a Handoff Summary with assumptions, risks, unresolved questions, evidence, stale artifacts, and next-stage instructions.
- Expanded the product graph node vocabulary so graph builds now include lifecycle coverage for discovery items, assumptions, hypotheses, buyers, stakeholders, strategy, requirements, domain concepts, bounded contexts, business rules, architecture components, tests, deployment artifacts, operation artifacts, contradictions, and learnings.
- Added graph metadata enrichment so every graph node carries statement type, confidence, source stage, and verification status, with low-confidence unresolved assumptions promoted to critical graph validation issues.
- Added `echel traceability` and `wiki/reports/traceability-matrix.md` so discovery, canon, strategy, requirement, domain, architecture, task, test, and evidence coverage is visible, including broken canon and evidence links.
- Added `wiki/validation/` artifacts for test strategy, acceptance, integration, e2e, security, performance, and validation reporting with requirement, task, domain, and acceptance-criteria mappings.
- Added `echel validate` to summarize validation artifacts, refresh validation reports, and add validation test/evidence target nodes to the product graph.

## Next

1. Add evidence registration and connect evidence artifacts into graph-backed traceability.
2. Add deployment and release readiness gates that consume validation output.
3. Expand release readiness into production operation and post-release learning loops.

## Risks/Blocks

- If execution/evidence schemas are adopted inconsistently, gate determinism will degrade.
- If new folders are added without a unique purpose, Echel may become harder for domain experts to navigate again.
- Force-generating from incomplete discovery remains risky; gates should keep treating template `TBD` content as incomplete.
- Requirements generation remains blocked until strategy is meaningful unless explicitly forced; the requirements gate now verifies the resulting artifacts before downstream domain work.
- Traceability reporting now surfaces missing canon graph links and absent evidence artifacts; validation now exposes evidence targets until TASK-0034 makes evidence registration executable.
