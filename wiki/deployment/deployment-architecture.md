---
type: deployment-artifact
stage: deployment
status: draft
owner: release
updated: 2026-07-12
---
# Deployment Architecture

## Purpose

This document defines how an Echel-managed product moves from a verified repository to a runnable environment. It is the deployment-stage source for topology, release boundaries, health checks, rollback compatibility, and operational handoff.

## Source Inputs

- Architecture overview: [[../architecture/overview]]
- Security architecture: [[../architecture/security-architecture]]
- Validation summary: [[../reports/validation-summary]]
- Evidence registry: `.echel/evidence_registry.json`
- Release plan: [[../roadmap/release-plan]]

## Deployment Model

| ID | Deployment Surface | Path | Runtime Boundary | Required Evidence | Status |
| --- | --- | --- | --- | --- | --- |
| DEP-001 | Echel Core CLI and wiki memory | Local product repository | Developer or product-owner workstation | Validation summary, graph validation, evidence registry | Draft |
| DEP-002 | Generated product repository baseline | `generated/product-repository/` | Local Python runtime and CI job | Unit test output, generated verification script result | Draft |
| DEP-003 | Future hosted or team runtime | Deferred until requirements justify it | External service boundary, tenant boundary, secret boundary | ADR, security review, operations runbook | Future |

## Topology

| Component | Deployable Unit | Environment | Dependency | Health Signal | Rollback Boundary |
| --- | --- | --- | --- | --- | --- |
| Product memory | `wiki/`, `.echel/`, schema, prompts, tools | Local / repository | Git checkout | `python3 tools/echel.py doctor` | Git revert or restored branch |
| Generated app baseline | `generated/product-repository/app` | Local / CI | Python standard library | `python app/main.py` and unit tests | Regenerate or revert generated output |
| Verification scripts | `generated/product-repository/scripts/verify.sh` and root lifecycle commands | Local / CI | Shell, Python | Script exit code and evidence record | Revert script or task commit |

## Deployment Path

1. Run validation and graph checks.
2. Register release evidence with `python3 tools/echel.py evidence add`.
3. Confirm deployment environment and secrets checklist.
4. Run the generated repository verification script.
5. Run release readiness once TASK-0036 implements the release gate.
6. Create release summary and proof pack.
7. Deploy or publish only if blockers are resolved or explicitly accepted.

## Deployment Constraints

- No credential, token, private key, or populated environment file may be committed.
- Hosted or shared deployment remains out of scope until a future ADR defines tenant, permission, backup, and operations boundaries.
- Deployment instructions must stay reproducible from committed documentation and local commands.

## Handoff To Release Gate

TASK-0036 must gate this artifact for a documented path, rollback boundary, secrets strategy, production checklist status, registered evidence, unresolved blockers, and accepted risk state.
