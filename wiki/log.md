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
- Added a canonical model for intelligence and memory compounding in `wiki/systems/project-intelligence-compounding-model.md`.
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
