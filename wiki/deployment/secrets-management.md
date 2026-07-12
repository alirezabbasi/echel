---
type: deployment-artifact
stage: deployment
status: draft
owner: security
updated: 2026-07-12
---
# Secrets Management

## Purpose

This document defines how secrets are identified, stored, used, rotated, and audited. It keeps product memory commit-safe and gives the release gate concrete secret-handling checks.

## Secret Classes

| ID | Secret Class | Examples | Allowed Storage | Prohibited Storage | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SEC-DEP-001 | Provider credentials | API keys, model provider tokens | Local environment, OS keychain, CI secret store | `wiki/`, committed `.env`, logs | Product Owner / Operator | Draft |
| SEC-DEP-002 | Deployment credentials | Cloud tokens, SSH keys, registry tokens | Secret manager or CI secret store | Repository files, screenshots, generated docs | Release Manager | Future |
| SEC-DEP-003 | Customer or production data secrets | Database passwords, webhook secrets | Managed secret store | Product memory, test fixtures | Operations Steward | Future |

## Handling Rules

- Commit only `.env.example` or placeholder configuration with non-secret values.
- Never paste real credentials into task packets, evidence summaries, logs, release notes, or screenshots.
- Secret names may be documented; secret values must not be documented.
- Rotation owner and rotation trigger must be known before production release.
- Any suspected exposure creates an incident or blocker before release approval.

## Release Checks

| Check | Required Evidence | Release Gate Behavior |
| --- | --- | --- |
| Secret inventory is current | Secret class table reviewed | Block if unknown secrets are required. |
| Secret values are not committed | Repository scan or review evidence | Block if committed secret value is found. |
| Runtime injection path is documented | Environment matrix and deployment architecture | Block if runtime cannot receive secrets safely. |
| Rotation path exists | Owner and trigger documented | Block for production unless accepted exception exists. |

## Handoff To Operations

Operations artifacts must define who can rotate secrets, where rotation is recorded, and how incidents are handled if a secret is exposed.
