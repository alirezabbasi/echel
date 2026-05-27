# Governance

This page defines the controls that keep Echel work traceable, verified, and repeatable.

## Delivery Controls

- Keep changes small and traceable.
- Align code, tests, and wiki updates in the same work cycle.
- Do not close tasks without verification evidence.
- Keep standards enforceable and update them when recurring defects appear.

## Gate Runner Contract

The gate runner provides a deterministic mechanism for evaluating whether a task or release can close.

### Gate Types

- `knowledge_gate`: required docs, wiki, and decision artifacts are current.
- `execution_gate`: lifecycle, state, and dependency rules are satisfied.
- `evidence_gate`: required proof artifacts are present and valid.
- `quality_gate`: tests, lint, and checks meet configured thresholds.
- `release_gate`: release-specific readiness checks pass.

### Evaluation Order

1. Knowledge gate
2. Execution gate
3. Evidence gate
4. Quality gate
5. Release gate, when applicable

### Determinism Rules

- Same inputs must produce identical verdicts.
- Non-deterministic external calls are forbidden unless captured as immutable artifacts first.
- Gate definitions must be versioned and referenced in outputs.

### Failure Semantics

- `fail`: gate evaluated and requirements were not met.
- `blocked`: gate could not evaluate because required inputs were missing.

Both outcomes must include explicit remediation hints.
