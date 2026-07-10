---
type: engineering-guide
stage: repository-factory
status: active
owner: engineering
updated: 2026-07-10
---
# Repository Structure

## Purpose

This document is the product-owned map of the repository baseline created by TASK-0024. It defines where product code belongs, which generated files are executable, and which memory surfaces agents must update when implementation changes the system.

## Source Inputs

- Product truth and lifecycle memory: `wiki/`
- Architecture boundaries: [[../architecture/overview]], [[../architecture/component-architecture]]
- Execution contract: [[../work/TASK_INDEX]]
- Factory report: [[../reports/repository-factory/generated-repository]]
- Generated baseline: `generated/product-repository/`

## Repository Map

```text
echel/
  wiki/                         product-owned durable memory
    engineering/               authoritative engineering operating guides
  tools/echel/                  Echel lifecycle and factory implementation
  tests/                        Echel Core regression tests
  generated/product-repository/
    README.md                   exact local command entry point
    app/                        generated application package and entry point
    config/                     checked-in configuration examples
    tests/                      generated product tests
    scripts/verify.sh           generated local verification gate
    docs/engineering/           generated convenience notes
    .github/workflows/ci.yml    generated CI verification baseline
    .env.example                non-secret environment contract
    pyproject.toml              Python baseline metadata
```

## Ownership Boundaries

| Surface | Authority | Change Rule |
| --- | --- | --- |
| `wiki/` | Product owner and lifecycle roles | Update when product intent, architecture, workflow, or state changes. |
| `wiki/engineering/` | Product engineering policy | Keep exact commands and repository rules synchronized with the generated baseline. |
| `tools/echel/` | Echel Core | Change when generation or lifecycle behavior changes. |
| `generated/product-repository/` | Repository factory output | Change the factory template as well as generated output so regeneration is idempotent. |
| `generated/product-repository/docs/engineering/` | Generated convenience documentation | Do not treat as a replacement for product-owned memory. |

## Structural Invariants

- Product memory remains under `wiki/`; generated code must not become the source of product truth.
- Application behavior belongs under `app/`; tests mirror observable behavior under `tests/`.
- Checked-in configuration contains examples and defaults only. Secrets and machine-specific values stay outside version control.
- Every executable local command in CI must also be available from `scripts/verify.sh` or the generated README.
- A generated-file change is incomplete if rerunning `python3 tools/echel.py repository-factory` would erase it.
- New top-level generated directories require an architecture or engineering decision with a clear owner and purpose.

## Current Entry Points

| Entry Point | Purpose | Command |
| --- | --- | --- |
| `app/main.py` | Run the local health-check baseline. | `python app/main.py` |
| `tests/test_health.py` | Verify the health-check contract. | `python -m unittest discover -s tests` |
| `scripts/verify.sh` | Run the complete generated baseline gate. | `./scripts/verify.sh` |

## Evolution Rule

Feature tasks may extend this structure only from an approved task packet. Any change to module boundaries, persistence, public interfaces, deployment posture, or configuration loading must update the relevant architecture document and create an ADR when it represents a major decision.
