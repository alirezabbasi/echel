---
type: deployment-artifact
stage: deployment
status: draft
owner: release
updated: 2026-07-12
---
# Environments

## Purpose

This document defines the environments where Echel artifacts are verified, released, or operated. It keeps local, CI, staging, and production responsibilities separate before release gates consume them.

## Environment Matrix

| ID | Environment | Purpose | Deployment Source | Data Boundary | Secrets Boundary | Promotion Rule | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ENV-001 | Local development | Build, verify, and inspect lifecycle artifacts. | Working tree | Local files only | `.env` or shell, never committed | Unit tests and graph validation pass | Active |
| ENV-002 | CI verification | Repeat deterministic checks outside the developer shell. | Git commit | Generated repository test fixtures | CI secret store if future jobs need secrets | CI jobs pass with no secret leakage | Draft |
| ENV-003 | Staging | Release rehearsal for generated products. | Tagged release candidate | Sanitized or synthetic data | Managed secret store | Production checklist passes in rehearsal | Future |
| ENV-004 | Production | Serve real product users or product owners. | Approved release | Production product memory and runtime data | Managed secret store with least privilege | Release gate passes or accepted exceptions exist | Future |

## Environment Separation Rules

- Local and CI may use fixtures, generated docs, and synthetic examples.
- Staging and production must not share writable state unless an ADR explicitly approves the risk.
- Production deployment requires a rollback plan, operations runbook, incident contact path, and registered release evidence.

## Configuration Expectations

| Setting Class | Local | CI | Staging | Production |
| --- | --- | --- | --- | --- |
| Non-secret defaults | Committed examples allowed | Committed examples allowed | Managed configuration | Managed configuration |
| Secrets | Local environment only | CI secret store | Secret manager | Secret manager |
| Test data | Fixtures allowed | Fixtures required | Sanitized data only | Real data only under policy |
| Logs | Local console and reports | CI logs | Centralized logs required | Centralized logs required |

## Handoff To Production Checklist

The production checklist must confirm which environments are in scope for the release, whether promotion rules passed, and whether any environment exceptions were accepted.
