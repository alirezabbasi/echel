# Architecture

Echel separates product truth from agent execution.

The accepted foundational choices and their tradeoffs are authoritative in the [architecture decision index](decisions/README.md). This page is a concise projection of those decisions.

```text
CLI / future UI
      │
Workflow service ─── Methodology stages
      │
FileStore ────────── Canonical Git-owned records
      │
ContextCompiler ──── Minimal work context
      │
AgentRuntime ─────── Hermes today, other adapters later
      │
VerificationRunner ─ Reproducible evidence
```

## Canonical state

A product repository contains `.echel/project.json`, `.echel/policy.json`, and record collections. These files are human-reviewable and versioned with product code.

There is no canonical generated graph. Relationships are explicit record identifiers. A future SQLite index may accelerate search, but it must remain disposable.

## Runtime boundary

`AgentRuntime` accepts a versioned task and context contract plus workspace and execution policy. Runtime adapters return normalized events and results. No Hermes storage format, provider API, prompt strategy, or internal Python API belongs in the Echel domain.

## Local operation and extensions

The core methodology, knowledge, planning, and verification workflows operate locally without a hosted Echel service. External systems retain authority for their own state and are referenced through explicit adapters.

Extensions implement narrow, versioned contracts outside the domain core. They cannot bypass policy, mutate canonical knowledge directly, or become required for opening and validating a project.

## Growth rule

New record types, services, reports, and interfaces require evidence from a real end-to-end workflow. Empty future-stage artifacts are never initialized.
