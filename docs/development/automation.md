# Automation OS Specification (v1)

## CLI contract

Target command surface:

- `echel ingest`
- `echel migrate`
- `echel lint`
- `echel gate`
- `echel readiness`
- `echel release-pack`

## Command responsibilities

- `ingest`: normalize external sources into canonical artifacts.
- `migrate`: map existing project structures to Echel schema.
- `lint`: validate structural and linking quality.
- `gate`: run deterministic closure/release gates.
- `readiness`: compute lifecycle readiness snapshot.
- `release-pack`: assemble release proof pack.

## Gate runner contract

Inputs:

- execution node graph
- applicable gate definitions
- evidence registry entries
- proof-pack documents

Outputs:

- machine-readable verdict (`pass | fail | blocked`)
- per-gate reasoning and missing evidence list
- timestamped run record for audit

## Agent playbooks by lifecycle phase

Each phase must define strict I/O contracts:

- required inputs
- allowed actions
- mandatory outputs
- evidence obligations
- handoff artifact for next phase

Phases:

- `idea`
- `discovery`
- `design`
- `build`
- `verify`
- `release`
- `operate`

## Adapter model

Adapters allow Echel adoption without repo rewrites.

### Adapter responsibilities

- Map local naming conventions to Echel node types.
- Register external evidence sources into the artifact registry.
- Provide compatibility shims for existing CI/task systems.
