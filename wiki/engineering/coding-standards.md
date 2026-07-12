---
type: engineering-guide
stage: repository-factory
status: active
owner: engineering
updated: 2026-07-10
---
# Coding Standards

## Baseline

The generated repository targets Python 3.11 or newer and intentionally starts with the standard library only. These standards keep early implementation small, inspectable, and easy for humans and AI agents to verify.

## Code Rules

- Use explicit module boundaries that follow [[../architecture/component-architecture]].
- Add `from __future__ import annotations` to new Python modules when annotations are used.
- Add type annotations to public functions and data structures.
- Keep entry points thin; domain or application behavior belongs in importable functions or modules.
- Prefer deterministic functions and explicit inputs over hidden global state.
- Use structured parsers for JSON, configuration, and other structured data.
- Raise or return specific failures; do not silently ignore invalid input.
- Do not add a dependency, framework, service, or background process without a task requirement and architecture rationale.
- Comments explain non-obvious intent or constraints, not line-by-line mechanics.

## Test Rules

- Every behavior change requires a test at the narrowest useful level.
- Tests must cover the happy path and relevant invalid or failure paths.
- Tests use `unittest` until an accepted decision changes the baseline.
- Tests must be deterministic, local, and independent of network access.
- A test name should describe the observable contract it proves.

## Baseline Lint And Quality Check

The dependency-free lint baseline is Python syntax compilation:

```bash
python -m compileall -q app tests
```

This command catches syntax and import-file compilation failures without introducing a package dependency. It is not a substitute for future formatting, type checking, security scanning, or richer linting. Adding those tools requires updating this document, the generated README, CI, and `scripts/verify.sh` in the same task.

## Required Local Gate

From `generated/product-repository/` run:

```bash
python -m compileall -q app tests
python -m unittest discover -s tests
python app/main.py
./scripts/verify.sh
```

The final script is the authoritative aggregate command. Direct commands remain documented so failures can be isolated.

## Documentation And Traceability

- Code changes must cite the active `TASK-####` in the task or commit context.
- Behavior changes update acceptance criteria and engineering docs when commands or boundaries change.
- Architecture-impacting changes update architecture memory before the task is marked done.
- Verification results become evidence through `python3 tools/echel.py evidence add`; records must include subject, kind, path, checksum, producer, and summary before task closure or release proof depends on them.

## Security Rules

- Never commit credentials, tokens, private keys, or populated `.env` files.
- Treat external input as untrusted and validate it at the boundary.
- Avoid logging secrets or full sensitive payloads.
- Security-sensitive behavior requires explicit tests and review scope.
