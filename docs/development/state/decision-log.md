# Decision Log

## DEC-0001

- Decision: Keep scaffold defaults domain-agnostic.
- Context: Scaffold is intended as reusable starting point across projects.
- Impact: Domain-specific content must be ingested later as raw sources.

## DEC-0002

- Decision: Adopt a multi-loop project intelligence compounding model (delivery, reliability, strategy) as a guiding operating framework.
- Context: Project needed an explicit method for turning accumulated knowledge into future direction guidance.
- Impact: Bug management, RCA, and synthesis cadence become mandatory intelligence inputs for roadmap and architecture decisions.

## DEC-0003

- Decision: Evolve Echel into a four-layer operating system with explicit Knowledge, Execution, Evidence, and Automation contracts.
- Context: Knowledge scaffolding alone is insufficient for full lifecycle delivery, verification, release readiness, and operations.
- Impact: Lifecycle states, typed execution graph, proof-pack evidence model, and deterministic gate orchestration become first-class project primitives.

## DEC-0004

- Decision: Generated projects are rooted at the target software repository, with Echel relocated to an internal `echel-core/` directory that is ignored by the target project's Git history.
- Context: Echel should initialize and drive development without becoming the primary artifact pushed to the target project's remote.
- Impact: Wizard outputs and usage guidance must treat the target project root as the implementation surface, while `echel-core` remains an internal orchestration layer.

## DEC-0005

- Decision: Simplify visible Echel folders around human-readable purposes: knowledge, decisions, work, reports, development state, and bugs.
- Context: The previous numbered development folders and fine-grained wiki taxonomy made the system feel more complex and repetitive than necessary.
- Impact: Tools, bootstrap paths, wiki links, and governance checks must use the simplified structure.

## DEC-0006

- Decision: Generated projects keep `wiki/` at the target project root while framework files live under `echel-core/`.
- Context: Product intelligence belongs to the product repository, while Echel methodology and automation belong to the framework.
- Impact: `project.echel` now includes `WIKI_ROOT`; generated `echel-core/project.echel` points it to `../wiki`.

## DEC-0007

- Decision: Adopt `docs/development/methodology.md` as the Echel vNext methodology contract.
- Context: The methodology needs to define Echel as an AI-native software engineering operating system, not only a documentation framework or product wiki scaffold.
- Impact: Future lifecycle schemas, commands, templates, graph nodes, stage gates, cockpit flows, and agent playbooks must align with the ordered lifecycle from Product Discovery Specification through operations and governance.

## DEC-0008

- Decision: Define product-level lifecycle stages in `schema/lifecycle-stage.schema.md`.
- Context: The vNext methodology contract needed a deterministic schema for stage IDs, required artifacts, gate conditions, transitions, and blocking rules before runtime stage evaluation can be built.
- Impact: Future readiness, graph, cockpit, and CLI work should use this schema as the product-stage contract while `schema/EXECUTION.md` remains focused on execution node behavior.

## DEC-0009

- Decision: Introduce `wiki/requirements/` as the vNext requirements model before requirements automation.
- Context: Echel needs a stable, human-readable bridge from discovery, canon, and strategy into domain, architecture, planning, implementation, QA, and release work.
- Impact: Requirements now use stable IDs, source links, priority, phase, dependencies, risks, acceptance criteria, and verification methods. TASK-0013 can build `echel requirements` on top of these structures, and TASK-0014 can add a readiness gate without inventing the model during implementation.

## DEC-0010

- Decision: Treat canon as the immediate source for strategy generation and reject template-only content as lifecycle progress.
- Context: Review of TASK-0003 through TASK-0011 found that strategy generation read directly from discovery, canon drift was only memory-backed, discovery gate coverage was narrower than intended, and generated canon/strategy files could contain `TBD` boilerplate presented as real content.
- Impact: Discovery gates now check operator, business value, and non-template research content; canon generation only promotes meaningful source sections; canon drift writes `wiki/canon/canon-drift.md` and stale markers; strategy templates and generation reference canon as their immediate upstream source while keeping discovery traceability.

## DEC-0011

- Decision: Generate requirements into explicit generated sections and graph manual nodes instead of overwriting hand-authored requirement model context.
- Context: TASK-0012 established human-readable requirement model documents, while TASK-0013 needed automation that derives requirements from canon and strategy.
- Impact: `echel requirements` preserves authored requirement guidance, writes generated requirement/NFR/MVP/OOS/acceptance sections, rejects vague source language, marks phases, and adds requirement nodes plus source edges to `wiki/graph.manual.json` before regenerating `wiki/graph.json`.

## DEC-0012

- Decision: Add `GATE-REQUIREMENTS` as a table-driven readiness gate in the shared gate engine.
- Context: TASK-0014 needed requirements to become an execution safety layer, not only Markdown artifacts. Downstream domain and architecture work should not proceed from MVP requirements that lack acceptance criteria, dependencies, risks, validation methods, explicit exclusions, or NFR coverage.
- Impact: `echel readiness --stage requirements` now evaluates requirement artifacts directly, the repo gate policy includes `GATE-REQUIREMENTS`, and generated requirements are checked for product graph coverage when generated IDs are present.

## DEC-0013

- Decision: Introduce `wiki/domain/` as technology-neutral product language and add `AGG-###` to the traceability schema for domain aggregates.
- Context: TASK-0015 needed first-class domain artifacts between requirements and architecture. Aggregates are required by the methodology, but the traceability schema previously defined domain concepts, bounded contexts, events, and rules without an aggregate ID family.
- Impact: Domain templates now map every current requirement and NFR to domain concepts, contexts, rules, workflows, events, and aggregates. Architecture work must preserve these domain boundaries, and future `echel domain` automation should generate or refresh rows without introducing implementation choices.

## DEC-0014

- Decision: Generate domain model updates into explicit generated sections and graph manual nodes.
- Context: TASK-0016 needed `echel domain` to build on the TASK-0015 templates without overwriting authored domain language. Domain generation must preserve requirement IDs, avoid technology choices, and make the requirement-to-domain chain visible in the product graph.
- Impact: `echel domain` refuses to run unless requirements readiness passes, unless `--force` is used. It writes generated domain rows for concepts, contexts, aggregates, events, workflows, and business rules, then upserts requirement and domain nodes plus mapping edges into `wiki/graph.manual.json`.

## DEC-0015

- Decision: Add `GATE-DOMAIN` as the architecture-entry consistency gate.
- Context: TASK-0017 needed domain modeling to become an execution safety layer, not only generated Markdown. Architecture must not proceed from undefined terms, duplicate meanings, unmapped requirements, missing generated graph nodes, or concrete technology choices hidden inside domain language.
- Impact: `echel readiness --stage domain` now validates domain artifacts before architecture work. The repository gate policy includes `GATE-DOMAIN`, and downstream architecture tasks can depend on a passed domain stage rather than only the presence of `wiki/domain/` files.

## DEC-0016

- Decision: Adopt `wiki/architecture/` as the expanded vNext architecture artifact model.
- Context: TASK-0018 needed architecture to become a full lifecycle stage after domain readiness, not a thin `architecture.md` summary. Roadmap, repository factory, task generation, validation, release, and operations need architecture surfaces that preserve domain boundaries and explain major choices.
- Impact: Architecture is now split into overview, context map, component, data, API, event, workflow, security, and observability documents. `ADR-0005` records the decision, and future `echel architecture` plus architecture gates should generate and validate against this expanded model while keeping `wiki/architecture.md` as a compatibility summary.

## DEC-0017

- Decision: Generate architecture mappings from gated domain coverage into dedicated generated sections.
- Context: TASK-0019 needed architecture automation to preserve authored TASK-0018 guidance while making requirement-to-domain-to-architecture traceability executable. Architecture generation should refuse unsafe inputs, suggest ADR coverage, and feed the product graph before roadmap work.
- Impact: `echel architecture` now refuses to run unless `GATE-DOMAIN` passes, unless `--force` is used. It writes generated `ARCH-9xx` rows across the architecture artifact surface, refreshes the compatibility `wiki/architecture.md` summary, and upserts architecture graph nodes plus requirement and domain mapping edges.

## DEC-0018

- Decision: Add `GATE-ARCHITECTURE` as the roadmap-entry architecture readiness gate.
- Context: TASK-0020 needed architecture to become an execution safety layer before roadmap planning. Roadmap generation must not proceed from missing deployment posture, incomplete data/security/observability models, untracked generated mappings, missing graph edges, or heavyweight architecture choices without ADR-backed rationale.
- Impact: `echel readiness --stage architecture` now validates the expanded architecture surface, accepted decision ADR coverage, generated `ARCH-9xx` requirement/domain mappings, architecture graph nodes and edges, and overengineering risk. The repository gate policy includes `GATE-ARCHITECTURE`, and TASK-0021 can depend on passed architecture readiness rather than artifact presence alone.

## DEC-0019

- Decision: Adopt `wiki/roadmap/` as the expanded vNext roadmap artifact model.
- Context: TASK-0021 needed roadmap to become a real architecture-to-execution handoff, not a thin `wiki/roadmap.md` list. Execution phase work must start from phased objectives, scope, dependencies, demos, risks, and exit gates so later task generation can stay small and verifiable.
- Impact: Roadmap is now split into master, MVP, architecture, engineering, and release roadmap documents. The root `wiki/roadmap.md` remains a compatibility summary, and TASK-0022 must consume the expanded roadmap artifacts when creating execution phase documents.

## DEC-0020

- Decision: Adopt `wiki/execution/` as the vNext execution phase artifact surface.
- Context: TASK-0022 needed the roadmap-to-execution handoff to become explicit before detailed task generation. Echel should not generate implementation tasks from roadmap prose; it needs phase-level task lists, dependencies, definition of done, validation commands, documentation obligations, and expected repo changes first.
- Impact: Execution planning is now split into foundation, MVP, hardening, production, and evolution phase documents. TASK-0023 must consume these phase artifacts when upgrading task generation into detailed `wiki/work/TASK-*.md` records and work packets.

## DEC-0021

- Decision: Generate agent-executable tasks from execution phase rows through `echel execution-tasks`.
- Context: TASK-0023 needed task generation to become a deterministic execution safety layer, not a manual translation from roadmap prose. Each phase task row already carries objective, business reason, scope, dependencies, acceptance, tests, validation, documentation updates, and expected repository changes.
- Impact: `tools/echel/execution.py` now parses `wiki/execution/`, enforces architecture readiness unless `--force` is used, writes one `wiki/work/TASK-1xxx-*.md` file per phase task, maintains `wiki/work/TASK_INDEX.md`, and refreshes the product graph so repository factory work can consume generated task records.

## DEC-0022

- Decision: Generate repository skeletons under `generated/product-repository/` through `echel repository-factory`.
- Context: TASK-0024 needed Echel to become a product-to-repository factory without confusing generated product baseline code with Echel Core runtime code. The repository skeleton should be inspectable, local-first, and derived from architecture artifacts plus generated execution tasks.
- Impact: `tools/echel/repository_factory.py` now enforces architecture readiness unless `--force` is used, requires generated execution tasks, writes app/config/test/CI/env/local-doc baseline files under `generated/product-repository/`, and records `wiki/reports/repository-factory/generated-repository.md`. TASK-0025 remains responsible for product-level engineering docs under `wiki/engineering/`.

## DEC-0023

- Decision: Use `wiki/engineering/` as the authoritative product engineering contract and keep generated engineering notes as reproducible convenience output.
- Context: TASK-0025 needed engineering documentation to guide real work on the TASK-0024 baseline without splitting authority between product memory and generated files. The baseline also lacked a runnable lint command.
- Impact: Repository structure, coding standards, development workflow, configuration strategy, and local development are now defined under `wiki/engineering/`. The dependency-free baseline lint is `python -m compileall -q app tests`, and the repository factory emits the same lint, test, and health-check contract in README, CI, generated local docs, and `scripts/verify.sh`. TASK-0026 roles must reference this workflow instead of redefining it.

## DEC-0024

- Decision: Adopt `wiki/agents/role-model.md` as the product-memory home of the vNext AI-agent role model, mirrored by `docs/development/methodology.md`, with every role expressed as responsibilities, inputs, outputs, and forbidden actions and bound to the shared `wiki/engineering/development-workflow.md` contract.
- Context: TASK-0026 needed Echel's virtual delivery team (Founder Interviewer through Governance Auditor) defined before playbooks and handoff protocols. The prior methodology section listed responsibilities and partial "must not" notes but did not satisfy the acceptance criterion that each role carry inputs and outputs.
- Impact: All 13 roles now declare a lifecycle-stage mapping and a four-part contract. Forbidden actions encode the execution-safety rules (no code before task packet, no assumptions as facts, no architecture while implementing unless asked, no task closure without evidence, no unrelated-file modification, no silent governance or non-negotiable exceptions). TASK-0027 (playbooks) and TASK-0028 (handoff protocol) build on this contract; EP2-001 and generated `wiki/work/TASK-1007` are done.

## DEC-0025

- Decision: Use `prompts/playbooks/` as the canonical lifecycle playbook source and make tool-specific prompt packs render from those playbooks instead of duplicating lifecycle behavior.
- Context: TASK-0027 needed canonical playbooks for discovery through governance after TASK-0026 defined bounded roles. Existing Codex, Claude Code, and Cursor prompts were thin per-tool instructions with no shared lifecycle rendering contract.
- Impact: Twelve lifecycle playbooks now define objective, primary role, required inputs, required outputs, guardrails, and canonical prompt text. Tool render maps under `prompts/codex/`, `prompts/claude-code/`, and `prompts/cursor/` map tool prompts to canonical playbooks, and implementation prompts enforce that product code cannot be written before an approved `wiki/work/TASK-*.md` task packet exists. TASK-0028 completed the explicit handoff protocol.

## DEC-0026

- Decision: Use `wiki/agents/handoff-protocol.md` as the required inter-role handoff contract for lifecycle stage outputs.
- Context: TASK-0028 needed a concrete handoff protocol after TASK-0026 defined roles and TASK-0027 defined playbooks. Without a required handoff shape, assumptions, risks, unresolved questions, evidence, and next-stage instructions could still be lost between AI roles.
- Impact: Every stage output must include a Handoff Summary with source artifacts, changed artifacts, decisions, assumptions, risks, unresolved questions, evidence, stale upstream artifacts, next-stage instructions, and blocking conditions. Canonical playbooks now require that summary, and EP2-002 / generated TASK-1008 are complete.
