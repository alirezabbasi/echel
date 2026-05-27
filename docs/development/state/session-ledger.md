# Session Ledger

## 2026-05-06

- Reframed scaffold identity to Echel.
- Removed domain-specific defaults.
- Added governance and memory controls.
- Added the Project Intelligence Compounding Model as a canonical system artifact.

## 2026-05-08

- Defined Echel as a four-layer operating system: Knowledge, Execution, Evidence, and Automation.
- Added v1 architecture and contract docs for lifecycle, typed execution nodes, evidence registry, proof packs, and deterministic gate running.
- Updated top-level project docs to make the four-layer model first-class.

## 2026-05-11

- Implemented v2 MVP foundation tooling in `tools/echel.py` and supporting modules.
- Added `project.echel` contract loading/validation and symbolic root resolution.
- Added workspace migration dry-run/apply flow with automatic rewrite and rollback manifest generation.
- Added coherence drift checks, evidence registry validation, and compiled policy gates in `echel doctor`.
- Began Phase 3 expansion by adding memory records/timeline querying, conformance fixture runner, migration wave planning, behavior contracts, and runtime adapter detection.
- Began Platform MVP Sprint 1 by adding a self-hosted FastAPI web runtime, SQLite-backed chat/provider storage, provider adapters, and web command bridge hooks.

## 2026-05-27

- Clarified Echel as a domain-expert-guided AI-native development platform.
- Simplified the visible folder structure so `wiki/` is organized by knowledge, decisions, work, and reports.
- Collapsed numbered development folders into direct operating files plus `state/` and `bugs/`.
- Updated tooling path constants and governance checks for the simplified structure.
- Updated project initialization so generated projects keep product `wiki/` at the repository root and place Echel methodology/tooling under `echel-core/`.
