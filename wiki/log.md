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
