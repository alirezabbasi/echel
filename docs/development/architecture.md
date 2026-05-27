# Echel Four-Layer OS Architecture (v1)

## Purpose

Define Echel as a full-lifecycle engineering operating system with four composable layers:

1. Knowledge OS
2. Execution OS
3. Evidence OS
4. Automation OS

This architecture is adapter-first so Echel can wrap existing repositories incrementally.

## Layer 1: Knowledge OS

### Scope

Persistent project knowledge and reasoning continuity.

### Canonical artifacts

- `wiki/` canonical pages and linked entities
- task artifacts and standards
- ADRs and decision records
- session and memory artifacts
- contradiction capture and resolution records

### Responsibilities

- Keep architecture, standards, and decisions durable and queryable.
- Preserve context across sessions and contributors.
- Synchronize conceptual changes into canonical wiki artifacts.

### Inputs and outputs

- Input: raw sources, implementation outcomes, decisions, incidents.
- Output: normalized knowledge artifacts used by all other layers.

## Layer 2: Execution OS

### Scope

Lifecycle orchestration and typed work management.

### Lifecycle model

`idea -> discovery -> design -> build -> verify -> release -> operate`

### Core capabilities

- Typed task graph (`epic`, `story`, `task`, `incident`, `rca`)
- Explicit dependencies and ownership
- Risk class (`low`, `medium`, `high`, `critical`)
- Definition of done and closure gates per node

### Responsibilities

- Convert intent into trackable, linked execution units.
- Enforce dependency correctness and closure discipline.
- Ensure lifecycle transitions have explicit evidence requirements.

## Layer 3: Evidence OS

### Scope

Durable, machine-readable proof for execution and release readiness.

### Artifact registry domains

- test evidence
- schema contracts
- runbooks
- SQL/data checks
- CI logs/results
- SLO/error-budget snapshots

### Core capabilities

- Registry index for non-wiki artifacts
- Proof pack per task/release (machine + human summary)
- Deterministic gate input contract

### Responsibilities

- Make completion claims auditable.
- Separate assertions from proof.
- Preserve verifiable traces for future RCA and audits.

## Layer 4: Automation OS

### Scope

Deterministic workflows and agent-executable operational contracts.

### Core capabilities

- CLI commands for ingest, migration, lint, gate, readiness
- Gate orchestration runner
- Agent playbooks for each lifecycle phase
- Project adapters for brownfield onboarding

### Responsibilities

- Reduce manual process variance.
- Standardize lifecycle execution across tools and agents.
- Enable gradual adoption in existing repos.

## Layer Interfaces

### Knowledge -> Execution

Execution nodes must link to canonical context pages and standards.

### Execution -> Evidence

Each closure gate declares required evidence artifact types.

### Evidence -> Automation

Gate runner consumes registry entries and proof packs deterministically.

### Automation -> Knowledge

Workflow outcomes update wiki/memory artifacts and session logs.

## Adoption strategy

1. Introduce schema/contracts first.
2. Add evidence registry and proof packs.
3. Enforce deterministic gates in CI/local workflows.
4. Enable adapter-based rollout across existing projects.

## Non-goals (v1)

- Replace existing CI providers.
- Force a single issue tracker.
- Require all teams to migrate historical artifacts at once.
