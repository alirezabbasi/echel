# Architecture

Echel separates product truth from agent execution.

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

`AgentRuntime` accepts a compiled prompt, workspace, model, toolsets, and metadata. Runtime adapters return normalized command output. No Hermes storage format or internal Python API belongs in the Echel domain.

## Growth rule

New record types, services, reports, and interfaces require evidence from a real end-to-end workflow. Empty future-stage artifacts are never initialized.
