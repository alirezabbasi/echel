---
type: log
status: active
---
# Log

## [2026-05-06] scaffold | echel baseline
- Established domain-agnostic Echel scaffold.
- Added governance, memory, and execution control artifacts.
- Hardened workflow automation and knowledge quality gates.

## [2026-05-06] model | project intelligence compounding
- Added a canonical model for intelligence and memory compounding in `wiki/knowledge/project-intelligence-compounding-model.md`.
- Defined delivery, reliability, and strategy loops with bug-management and RCA feedback paths.
- Added maturity stages, operating cadence, decision guidance protocol, and measurement model for direction shaping.

## [2026-05-08] architecture | four-layer os
- Defined Echel as a four-layer operating system: Knowledge OS, Execution OS, Evidence OS, and Automation OS.
- Added v1 architecture and contract docs covering lifecycle states, typed task graph, artifact registry, proof packs, and deterministic gate running.
- Updated execution and memory artifacts so rollout is traceable and operationally visible.

## [2026-05-10] repo-model | target-root-with-internal-echel-core
- Clarified generated project topology: target software repository is the root artifact, with Echel relocated under `echel-core/`.
- Updated guidance so implementation happens at target project root while orchestration remains in `echel-core`.
- Recorded decision to keep `echel-core` out of target-project Git history via `.gitignore`.

## [2026-05-11] release-2 | v2-mvp-foundation
- Added declarative `project.echel` contract loading and validation.
- Added path abstraction roots and migration-map rewrite support with dry-run/apply workspace move flow and rollback manifests.
- Added `echel` core commands: `start`, `doctor`, `close-task`, and `sync-memory`.
- Added coherence drift checks, evidence registry validation/linkage checks, and compiled gate policy execution.

## [2026-05-11] release-2 | phase-3-expansion-started
- Added durable memory kernel records (`.echel/memory_records.jsonl`) with contradiction-aware querying commands.
- Added differential conformance runner with fixture definitions and generated analysis report output.
- Added migration wave planner for phased rollout suggestions with task dependency/risk scoring.
- Added workspace move safety rails requiring impact preview before apply (unless forced).
- Added LLM behavior contract checks and initial Python/TypeScript runtime adapter discovery hooks.

## [2026-05-11] platform | sprint-1-self-hosted-web-interface
- Added `echel platform init` and `echel platform up` CLI commands.
- Added FastAPI-based self-hosted web runtime with local SQLite storage for providers, threads, and messages.
- Added provider adapter layer for `openai`, `anthropic`, and `openai_compatible` endpoints.
- Added minimal web UI for provider connection, thread creation, and chat, including `/echel ...` command bridge for safe command subset.

## [2026-05-27] product-framing | ai-native-domain-expert-platform
- Clarified Echel as a platform for AI-native software development through advanced vibe coding workflows guided by domain experts and AI agents.
- Reframed persistent memory as the solution to AI agent token/context limitations across long-running development.
- Defined the ownership boundary between `wiki/` durable project intelligence and `docs/development/` operating procedure.
- Added `TASK-0005` to simplify overlapping knowledge and development documentation surfaces.

## [2026-05-27] structure | human-readable-folder-model
- Consolidated wiki folders into `knowledge`, `decisions`, `work`, and `reports`.
- Collapsed numbered development subfolders into direct files plus `state` and `bugs`.
- Moved raw source files and conformance fixtures up one level to remove unnecessary nesting.
- Added ADR-0003 to preserve the simplified folder model as an intentional product decision.

## [2026-05-27] initialization | product-wiki-at-project-root
- Updated project initialization so generated repositories keep `wiki/` at the product root.
- Kept Echel framework files, SDLC methodology, prompts, schemas, tools, and operating docs inside `echel-core/`.
- Added `WIKI_ROOT` to project configuration so tools can run from `echel-core/` while updating product-owned memory.
- Added ADR-0004 to preserve the product-wiki/framework-core boundary.

## [2026-05-27] strategy | v2-product-direction-review
- Reviewed Echel's architecture, workflow, documentation model, tooling, prompts, platform runtime, and current project direction.
- Added `wiki/reports/echel-v2-product-direction-review.md`.
- Recommended V2 evolve from framework scaffold into a guided product-creation platform for domain-expert-led AI-native development.

## [2026-05-27] phase-1 | product-flow-commands
- Started V2 Phase 1 by adding product-first initialization pages.
- Added `echel define`, `echel clarify`, `echel plan`, `echel status`, and `echel next`.
- Added Make targets for the product-owner command surface.

## [2026-05-27] phase-1 | completion
- Completed Phase 1 product workflow tasks TASK-0007 through TASK-0013.
- Added interactive clarification answers, MVP planning synthesis, readiness status, agent work packets, product-first generated wiki cleanup, Phase 1 guide, and `make verify-phase1`.

## [2026-05-27] define | product-flow
- Updated product definition through `echel define`.

## [2026-05-27] phase-2 | product-graph-foundation
- Added product graph extraction, storage, validation, summary, and report generation.
- Added graph-aware `status` and planning report refresh.
- Added relationship commands for features, risks, and manual links.
- Added `make verify-phase2` to validate the graph workflow inside generated projects.

## [2026-05-28] phase-3 | graph-backed-agent-work
- Added graph-backed agent work packets through `echel build`.
- Added review reports through `echel review`.
- Added packet and review schemas, evidence obligations, memory update checklists, and graph-aware next-task selection.
- Added `make verify-phase3` to validate the build/review loop inside generated projects.

## [2026-05-28] phase-4 | product-cockpit
- Added cockpit snapshot and safe command APIs for product state and product actions.
- Replaced the chat-first platform UI with a cockpit-first interface covering dashboard, clarifications, roadmap, work, graph, packets, reviews, risks, decisions, and chat.
- Added cockpit API schema, Phase 4 guide, and `make verify-phase4`.

## [2026-05-28] phase-5 | readiness-and-proof-packs
- Added milestone/release targets, readiness reports, proof packs, and release summaries.
- Added readiness gates for graph integrity, evidence coverage, risks, and review state.
- Added cockpit readiness data and view.
- Added `make verify-phase5`.

## [2026-05-28] audit | v2-requirements-hardening
- Audited Echel against the seven requested V2 capability areas.
- Added `steer`, richer product-first initialization, workflow/evidence graph nodes, likely files in packets, and cockpit architecture/contradiction/activity views.
- Added `wiki/reports/v2-requirements-hardening-audit.md`.

## [2026-05-28] docs | product-facing-readme
- Rewrote `README.md` as a marketing/product overview for Echel.
- Moved technical setup, command reference, cockpit launch, verification, and operating-method links into `docs/technical-quick-start.md`.

## [2026-07-02] methodology | vnext-contract
- Added `docs/development/methodology.md` as the canonical vNext lifecycle contract.
- Defined source-of-truth hierarchy, lifecycle stages, stage gates, traceability expectations, and AI-agent role boundaries.
- Updated development state and decision log so downstream vNext tasks use the methodology contract as their source of truth.

## [2026-07-02] schema | lifecycle-stage-contract
- Added `schema/lifecycle-stage.schema.md` for deterministic vNext stage definitions.
- Defined canonical stage IDs, required artifacts, gate conditions, allowed transitions, blocking rules, readiness statuses, and backward-transition reason artifacts.
- Clarified that `schema/EXECUTION.md` governs execution nodes while the new lifecycle schema governs product-stage readiness.

## [2026-05-27] clarify | product-flow
- Answered `mvp` clarification.

## [2026-05-27] clarify | product-flow
- Answered `needs` clarification.

## [2026-05-27] clarify | product-flow
- Answered `components` clarification.

## [2026-05-27] packet | product-flow
- Generated work packet [[reports/work-packets/TASK-0001-initialize-project-wiki-packet]].

## [2026-05-27] review | product-flow
- Generated review report [[reports/reviews/TASK-0001-initialize-project-wiki-review]].

## [2026-05-28] milestone | readiness
- Updated release `MVP`.

## [2026-05-28] release | readiness
- Generated release summary [[reports/releases/mvp-release-summary]].

## [2026-05-28] readiness | readiness
- Generated readiness report [[reports/readiness/mvp-readiness]].

## [2026-05-28] readiness | readiness
- Generated readiness report [[reports/readiness/mvp-readiness]].

## [2026-05-28] proof-pack | readiness
- Generated proof pack [[reports/proof-packs/mvp-proof-pack]].

## [2026-05-28] steer | product-flow
- Steered `workflow`.

## [2026-05-28] packet | product-flow
- Generated work packet [[reports/work-packets/TASK-0001-initialize-project-wiki-packet]].

## [2026-05-28] release | readiness
- Generated release summary [[reports/releases/mvp-release-summary]].

## [2026-05-28] readiness | readiness
- Generated readiness report [[reports/readiness/mvp-readiness]].

## [2026-05-28] proof-pack | readiness
- Generated proof pack [[reports/proof-packs/mvp-proof-pack]].

## [2026-05-28] readiness | readiness
- Generated readiness report [[reports/readiness/mvp-readiness]].

## [2026-05-28] packet | product-flow
- Generated work packet [[reports/work-packets/TASK-0001-initialize-project-wiki-packet]].

## [2026-07-02] schema | traceability
- Added `schema/traceability.schema.md` as the vNext methodology ID system.
- Defined 36 ID families covering discovery through operations artifacts.
- Specified naming rules, artifact object shapes, stage mappings, and traceability chains.
- Planned six-phase validation logic: format, reference integrity, stage coverage, chain completeness, statement discipline, supersession.
- Defined graph integration with trace_id index and matrix structure.

## [2026-07-02] discovery | product-discovery
- Added `wiki/discovery/product-discovery-spec.md` as the PDS template with 25 sections.
- Added `wiki/discovery/research-plan.md` tracking research across market, technology, legal, domain, and competition.
- Added `wiki/discovery/assumptions.md` tracking assumptions, hypotheses, open questions, and resolved items.
- Template includes statement type, confidence, and traceability ID fields for every important entry.
- Quality gate checklist blocks progression to Product Canon if required items are missing.

## [2026-07-02] discover | discovery
- Added `echel discover` CLI command with `tools/echel/discovery.py` module.
- Command initializes discovery files, reports readiness percentage, lists open questions.
- Command updates 28 discoverable PDS fields via `--field` and `--value` arguments.
- Log entries appended to `wiki/log.md` with discovery label.

## [2026-07-02] gate | discovery
- Added `GATE-DISCOVERY` gate check in `tools/echel/gates.py` validating required discovery fields.
- `echel readiness --stage discovery` reports PASS or BLOCKED with remediation messages.
- `echel doctor` now includes GATE-DISCOVERY in gate evaluation output.
- Later remediation expanded the gate to cover operator, measurable business value, and non-template research content.

## [2026-07-02] canon | product-canon
- Added `wiki/canon/product-canon.md` as the primary source of product truth.
- Added `wiki/canon/vision.md` defining vision statement, business transformation, and non-goals.
- Added `wiki/canon/product-principles.md` defining core principles and decision framework.
- Added `wiki/canon/non-negotiables.md` defining hard constraints and requirements.
- Every canon file includes discovery ID references and quality gate checklists.

## [2026-07-02] canon | canon
- Added `echel canon` CLI command with `tools/echel/canon.py` module.
- Command refuses to run when discovery gate fails unless --force is used.
- Command generates or refreshes canon files from PDS with discovery content.
- Command reports canon status showing which files have TBD sections.
- Later remediation prevents template-only `TBD` discovery sections from being promoted into canon as product truth.

## [2026-07-02] canon-drift | canon
- Added `echel canon-drift` CLI command detecting contradictions between discovery and canon.
- Contradictions are recorded as durable memory records with type `canon-drift`.
- Canon sections are marked stale when discovery fields have been updated.
- Later remediation added durable `wiki/canon/canon-drift.md` artifact entries for detected drift.

## [2026-07-02] strategy | product-strategy
- Added `wiki/strategy/icp.md` defining primary and secondary ICP with demographics, behavioral signals, pain indicators, and anti-ICP.
- Added `wiki/strategy/buyer-user-model.md` separating 6 stakeholder roles: economic buyer, user, approver, influencer, blocker, and operator.
- Added `wiki/strategy/market-wedge.md` defining the specific market entry point with pain intensity, urgency, willingness to pay, switching cost ratings.
- Added `wiki/strategy/competitive-analysis.md` mapping direct competitors, indirect competitors, non-software alternatives, and "do nothing".
- Added `wiki/strategy/positioning.md` defining positioning statement, category design, messaging framework, and brand personality.
- Added `wiki/strategy/pricing-and-packaging.md` defining pricing model, tiers, packaging strategy, and revenue projections with hypothesis marking.
- Added `wiki/strategy/pmf-evidence.md` defining continue/stop criteria, evidence types, collection phases, and decision framework.
- Later remediation added explicit canon references to every strategy artifact while preserving discovery references.

## [2026-07-02] strategy | strategy
- Added `echel strategy` CLI command with `tools/echel/strategy.py` module.
- Command refuses to run when discovery gate fails unless --force is used.
- Command generates or refreshes 7 strategy files from canon-derived content.
- Command reports strategy status showing which files have TBD sections.
- Added `echel strategy-readiness` CLI command reporting pass/block state with remediation messages.

## [2026-07-02] review-remediation | lifecycle
- Re-reviewed TASK-0003 through TASK-0011 against their objectives and acceptance criteria.
- Hardened discovery gating, canon generation, canon drift durability, and canon-driven strategy generation.
- Cleaned previously generated template noise from canon and strategy wiki artifacts.
- Added regression tests in `tests/test_vnext_lifecycle.py`.

## [2026-07-02] requirements | requirement-model
- Added `wiki/requirements/product-requirements.md` as the primary product requirement register.
- Added `wiki/requirements/functional-requirements.md` and `wiki/requirements/non-functional-requirements.md` with testable requirement fields.
- Added `wiki/requirements/mvp-scope.md` to separate MVP scope from later phases.
- Added `wiki/requirements/out-of-scope.md` to record explicit exclusions and revisit triggers.
- Added `wiki/requirements/acceptance-criteria.md` to map `REQ-###` and `NFR-###` items to verifiable criteria.
- Preserved source links to discovery, canon, strategy, and traceability artifacts for downstream automation.

## [2026-07-02] requirements | requirements
- Added `echel requirements` CLI command with `tools/echel/requirements.py` module.
- Command initializes requirement artifacts, reports generated requirement status, and refuses to generate when strategy readiness fails unless `--force` is used.
- Requirements are generated from canon and strategy into dedicated generated sections without replacing hand-authored model guidance.
- Generated requirements include priority, phase, source IDs, dependencies, risks, acceptance criteria, and validation methods.
- Vague upstream source language is rejected before requirement rows are written.
- Requirement and NFR nodes plus source edges are added to the product graph through `wiki/graph.manual.json`.

## [2026-07-02] gate | requirements
- Added `GATE-REQUIREMENTS` in `tools/echel/gates.py`.
- `echel readiness --stage requirements` validates MVP requirement testability, acceptance criteria, dependencies, risks, source IDs, explicit out-of-scope records, MVP non-functional requirements, and generated requirement graph coverage.
- Added the requirements gate to `.echel/gates.json` so `echel doctor` includes it with the other lifecycle gates.
- Added regression tests for passing generated requirements, missing graph coverage, and missing acceptance criteria.

## [2026-07-02] domain | domain-model
- Added `wiki/domain/domain-overview.md` with domain modeling rules, technology-neutral guardrails, and requirement-to-domain coverage.
- Added `wiki/domain/ubiquitous-language.md`, `bounded-contexts.md`, `entities.md`, `aggregates.md`, `domain-events.md`, `workflows.md`, and `policies-and-rules.md`.
- Mapped current `REQ-###` and `NFR-###` rows to `DM-###`, `BC-###`, `AGG-###`, `DE-###`, and `BR-###` domain artifacts.
- Added `AGG-###` to `schema/traceability.schema.md` for domain aggregate traceability.

## [2026-07-01] discover | discovery
- Updated `problem-statement` in Product Discovery Specification.

## [2026-07-01] canon | canon
- Generated or refreshed Product Canon from discovery.

## [2026-07-01] strategy | strategy
- Generated or refreshed Product Strategy from canon.

## [2026-07-02] domain | domain
- Added `echel domain` CLI command with `tools/echel/domain.py` module.
- Command refuses to run when requirements readiness fails unless `--force` is used.
- Command generates or refreshes domain sections from requirement rows without replacing hand-authored domain guidance.
- Generated rows include `DM-###`, `BC-###`, `AGG-###`, `DE-###`, `WF-DM-###`, and `BR-###` IDs linked back to `REQ-###` and `NFR-###`.
- Requirement and domain nodes plus mapping edges are added to the product graph through `wiki/graph.manual.json`.

## [2026-07-02] gate | domain
- Added `GATE-DOMAIN` in `tools/echel/gates.py`.
- `echel readiness --stage domain` validates requirement-to-domain coverage, undefined domain ID references, duplicate meanings, generated domain graph coverage, and concrete technology leakage.
- Added the domain gate to `.echel/gates.json` so `echel doctor` includes it with the other lifecycle gates.
- Added regression tests for passing generated domain models, unmapped requirements, undefined references, duplicate meanings, and technology leakage.

## [2026-07-02] architecture | artifact-model
- Added `wiki/architecture/` with overview, context map, component, data, API, event, workflow, security, and observability architecture documents.
- Added `ADR-0005` to record the vNext architecture artifact model decision.
- Updated `wiki/architecture.md` as a compatibility summary linking to the expanded architecture surface.
- Architecture artifacts now carry `ARCH-###` rows, source IDs, rationale, ADR coverage, domain boundary mappings, and downstream handoff notes.

## [2026-07-02] architecture | architecture
- Generated or refreshed 11 architecture mappings from domain coverage.

## [2026-07-05] gate | architecture
- Added `GATE-ARCHITECTURE` in `tools/echel/gates.py`.
- `echel readiness --stage architecture` validates architecture artifacts, deployment posture, data/security/observability models, ADR coverage, generated requirement/domain mappings, graph coverage, and overengineering risk.
- Added the architecture gate to `.echel/gates.json` so `echel doctor` includes it with the other lifecycle gates.
- Added regression tests for passing generated architecture, missing graph nodes, missing security model, and unjustified complexity.

## [2026-07-10] roadmap | artifact-model
- Added `wiki/roadmap/` with master, MVP, architecture, engineering, and release roadmap documents.
- Updated `wiki/roadmap.md` as a compatibility summary linking to the expanded roadmap surface.
- Roadmap artifacts now carry phase objectives, scope, out-of-scope, dependencies, demo scenarios, risks, exit gates, source IDs, and downstream handoff notes for execution planning.

## [2026-07-10] execution | phase-artifacts
- Added `wiki/execution/` with foundation, MVP, hardening, production, and evolution phase documents.
- Execution phase artifacts now carry phase task IDs, task lists, dependencies, acceptance criteria, tests, validation commands, documentation updates, definition of done, and expected repository changes.
- Updated roadmap status so TASK-0023 can consume phase artifacts when generating detailed agent-executable tasks.

## [2026-07-10] execution | task-generation
- Added `tools/echel/execution.py` and the `python3 tools/echel.py execution-tasks` command.
- Task generation now requires architecture readiness unless `--force` is used for draft generation.
- Generated 20 agent-executable `wiki/work/TASK-1xxx-*.md` records plus `wiki/work/TASK_INDEX.md` from the execution phase task rows.
- Generated tasks include objective, business reason, technical scope, files, dependencies, instructions, acceptance criteria, tests, validation command, rollback notes, documentation updates, definition of done, and out-of-scope.

## [2026-07-10] repository-factory | skeleton
- Added `tools/echel/repository_factory.py` and the `python3 tools/echel.py repository-factory` command.
- Repository generation now requires architecture readiness and generated execution tasks unless `--force` is used for draft generation.
- Generated `generated/product-repository/` with app, config, tests, CI workflow, environment example, verification script, and generated engineering docs.
- Added `wiki/reports/repository-factory/generated-repository.md` to record repository factory inputs and outputs.

## [2026-07-10] engineering | operating-docs
- Added `wiki/engineering/` guides for repository structure, coding standards, development workflow, configuration strategy, and local development.
- Established product-owned engineering docs as authoritative over generated convenience notes.
- Added the dependency-free `python -m compileall -q app tests` lint baseline to the generated README, CI, local docs, verification script, and repository-factory regression coverage.
- Marked EP1-002 and generated TASK-1005 done; TASK-0026 can now bind AI-agent roles to the shared engineering workflow.

## [2026-07-11] agent-roles | role-model
- Defined Echel's virtual delivery team in `wiki/agents/role-model.md` and mirrored it in `docs/development/methodology.md` under `## AI-Agent Role Model`.
- Expanded all 13 roles (Founder Interviewer, Business Analyst, Product Manager, Strategy Analyst, Domain Modeler, Solution Architect, Delivery Planner, Implementation Agent, QA Agent, Security Reviewer, Release Manager, Operations Steward, Governance Auditor) from responsibility-only bullets into a four-part contract: responsibilities, inputs, outputs, and forbidden actions.
- Added a lifecycle-stage mapping table and bound every role to the shared `wiki/engineering/development-workflow.md` contract, satisfying the TASK-0025 dependency.
- Added `test_agent_role_model_has_required_sections` to `tests/test_vnext_lifecycle.py` asserting each role renders the four required subsections.
- Marked TASK-0026, EP2-001, and generated TASK-1007 done; updated decision log (DEC-0024), current-state, where-are-we, work KANBAN, and generated execution artifacts.

## [2026-07-11] playbooks | lifecycle-prompts
- Added canonical lifecycle playbooks under `prompts/playbooks/` for discovery, canon, strategy, requirements, domain, architecture, roadmap, execution, validation, release, operations, and governance.
- Added tool render maps for Codex, Claude Code, and Cursor so tool-specific prompts derive lifecycle behavior from canonical playbooks.
- Updated implementation prompts to render `prompts/playbooks/execute.md` and enforce the approved task-packet requirement before product implementation code.
- Recorded DEC-0025 and added regression coverage for playbook existence, required sections, render maps, and no-code-before-task-packet guardrails.

## [2026-07-11] handoffs | agent-protocol
- Added `wiki/agents/handoff-protocol.md` as the required inter-role handoff protocol for lifecycle stage outputs.
- Defined the required Handoff Summary fields: roles, stage, source artifacts, changed artifacts, decisions, assumptions, risks, unresolved questions, evidence, stale upstream artifacts, next-stage instructions, and blocking conditions.
- Updated every canonical lifecycle playbook to require a Handoff Summary using the protocol.
- Marked EP2-002 and generated TASK-1008 done; recorded DEC-0026 and added regression coverage for the protocol and playbook handoff requirement.

## [2026-07-11] graph | lifecycle-node-types
- Expanded product graph extraction with first-class lifecycle node types for discovery items, assumptions, hypotheses, buyers, stakeholders, strategy, requirements, domain concepts, bounded contexts, business rules, architecture components, tests, deployment artifacts, operation artifacts, contradictions, and learnings.
- Updated product graph schema, traceability notes, methodology, and graph guide docs so the graph reflects Echel's full AI-native software engineering methodology rather than only product/task memory.
- Added regression coverage proving lifecycle node types appear in generated graph builds while graph validation remains passing.
- TASK-0029 is complete; TASK-0030 remains responsible for statement type, confidence, source-stage, verification-status, and trace ID metadata.

## [2026-07-12] graph | statement-metadata
- Added graph metadata enrichment for `trace_id`, `statement_type`, `confidence`, `source_stage`, and `verification_status`.
- Updated graph validation so missing metadata is reported and unresolved low-confidence assumptions become critical graph integrity issues.
- Updated product graph schema, traceability notes, methodology, state docs, roadmap summary, EP2-003, TASK-1009, and TASK_INDEX to reflect completed graph lifecycle coverage.
- TASK-0030 is complete; TASK-0031 can build the traceability matrix on top of lifecycle nodes and metadata.

## [2026-07-12] traceability | lifecycle-matrix
- Added `python3 tools/echel.py traceability`.
- Generated `wiki/reports/traceability-matrix.md` with discovery -> canon -> strategy -> requirement -> domain -> architecture -> task -> test -> evidence coverage, stage totals, artifact families, graph integrity notes, and broken-chain details.
- Marked EP2-004, TASK-1010, RM-005, ENG-005, REL-005, and ARCH-204 done.
- TASK-0031 is complete; validation and evidence registration are the next lifecycle hardening tasks.

## [2026-07-12] validation | artifact-surface
- Added `wiki/validation/` with test strategy, acceptance, integration, e2e, security, performance, and validation report artifacts.
- Validation artifacts map tests to requirement IDs, task IDs, domain concepts, acceptance criteria, and future evidence targets.
- Marked EP3-001 and generated TASK-1011 done.
- TASK-0032 is complete; TASK-0033 should implement the validation command by summarizing these artifacts.

## [2026-07-12] validation | command
- Added `python3 tools/echel.py validate`.
- Validation now writes `wiki/reports/validation-summary.md`, refreshes `wiki/validation/validation-report.md`, reports passed, failed, skipped, blocked, risks, and blockers, and upserts validation test/evidence target nodes into the product graph.
- Marked EP3-002 and generated TASK-1012 done.
- TASK-0033 is complete; TASK-0034 evidence registration is the next validation/evidence task.

## [2026-07-12] evidence | registration-command
- Added `python3 tools/echel.py evidence add`.
- Evidence registration now records subject, kind, path, checksum, producer, and summary without hand-editing `.echel/evidence_registry.json`.
- Evidence registration refreshes graph evidence nodes, and task closure remains blocked unless referenced evidence IDs exist in the registry.
- Marked EP3-003, generated TASK-1013, and ENG-006 done; deployment and release gates are the next production hardening tasks.

## [2026-07-12] deployment | artifact-surface
- Added `wiki/deployment/` with deployment architecture, environments, release process, rollback plan, secrets management, and production checklist artifacts.
- Product graph generation now includes deployment documents as deployment-stage artifact nodes.
- Updated validation/security notes so release gate blockers now point to TASK-0036 rather than missing deployment docs.
- TASK-0035 is complete; TASK-0036 should turn validation, evidence, deployment docs, risks, and blockers into an executable release gate.

## [2026-07-12] release | readiness-gate
- Added `GATE-RELEASE` and `python3 tools/echel.py readiness --stage release`.
- Release readiness now checks validation reports and open blockers, deployment artifacts, rollback rows, production checklist status, registered evidence, and release risk mitigation or acceptance.
- Marked EP3-004 and generated TASK-1014 done.
- TASK-0036 is complete; TASK-0037 operations artifacts are the next production hardening task.

## [2026-07-13] operations | artifact-surface
- Added `wiki/operations/` with runbook, observability, incident response, backup and recovery, SLA/SLO, change management, and evolution backlog artifacts.
- Operations docs define support ownership, incident severity and escalation, recovery objectives, service expectations, change governance, and learning backlog intake.
- Product graph generation now includes operations documents as operations-stage `operation-artifact` nodes.
- Marked EP3-005 and generated TASK-1015 done; TASK-0038 learning loop is the next operations/evolution task.
