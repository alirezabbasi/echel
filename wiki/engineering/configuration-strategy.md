---
type: engineering-guide
stage: repository-factory
status: active
owner: engineering
updated: 2026-07-10
---
# Configuration Strategy

## Purpose

Configuration must make environment differences explicit without placing secrets or machine-specific state in version control.

## Current Configuration Surfaces

| Surface | Purpose | Committed | Runtime Loading |
| --- | --- | --- | --- |
| `.env.example` | Documents supported environment keys and safe sample values. | Yes | Not implemented in the baseline. |
| `.env` | Local secret or machine-specific overrides. | No | Not implemented in the baseline. |
| `config/settings.example.json` | Documents structured application settings. | Yes | Not implemented in the baseline. |
| Process environment | Future runtime override surface. | No | Not implemented in the baseline. |
| `pyproject.toml` | Python and repository metadata. | Yes | Read by Python tooling. |

The current health-check application has no configurable runtime behavior. Example files are contracts for later tasks, not evidence that configuration loading already exists.

## Intended Precedence

When runtime configuration is introduced, use this order from highest to lowest precedence:

1. Explicit command-line arguments, when supported.
2. Process environment variables.
3. Local `.env` values for development only.
4. Checked-in non-secret defaults.

The implementation task that activates this precedence must validate values, define required keys, add failure-path tests, and update architecture if configuration ownership changes.

## Key Rules

- Use uppercase snake case for environment keys, such as `APP_ENV` and `LOG_LEVEL`.
- Keep `.env.example` complete, non-secret, and safe to commit.
- Never place real credentials or production values in examples, tests, logs, or documentation.
- Fail clearly when a required value is missing or invalid.
- Parse values into typed application settings at one boundary instead of reading environment variables throughout the codebase.
- Separate local, test, staging, and production values; do not encode environment branching in business logic.
- Document every new key, default, allowed values, owner, and restart implications.

## Local Setup

From `generated/product-repository/`:

```bash
cp .env.example .env
```

This copy is optional for the current baseline because the application does not load `.env`. The file is ignored by Git and reserved for later configuration tasks.

## Change Checklist

- Update `.env.example` or `config/settings.example.json`.
- Update this strategy and [[local-development]].
- Add tests for defaults, overrides, missing required values, and invalid values.
- Confirm secrets remain untracked.
- Run `./scripts/verify.sh`.
