---
type: api-architecture
stage: architecture
status: draft
owner: architecture
updated: 2026-07-02
---
# API Architecture

## Purpose

API architecture defines command, local cockpit, and future agent integration contracts. It does not require a public network API unless later architecture decisions justify one.

## Interaction Surfaces

| ID | Surface | Consumer | Contract | Source IDs | Rationale | ADR Coverage | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ARCH-401 | CLI Command Surface | Product owner, AI agent, scripts | `python3 tools/echel.py <command>` with deterministic exit codes and file outputs | REQ-005, REQ-006, NFR-005 | CLI is scriptable, auditable, and compatible with local repositories. | ADR-0002, ADR-0005 | Existing |
| ARCH-402 | Stage Gate Interface | Lifecycle commands and operator checks | `readiness --stage <stage>` returning PASS or BLOCKED with failures | REQ-003, REQ-004, NFR-003 | Stage gates make methodology enforceable. | ADR-0002, ADR-0005 | Existing |
| ARCH-403 | Graph Interface | Status, packets, reports, cockpit | `graph build`, `graph validate`, `graph report`, generated JSON | REQ-001, NFR-002 | Graph traversal needs deterministic local artifacts. | ADR-0002 | Existing |
| ARCH-404 | Cockpit Command Bridge | Local cockpit | Safe command invocation over local runtime | REQ-006, NFR-005 | Cockpit should steer existing commands rather than duplicate logic. | ADR-0004 | Existing |
| ARCH-405 | Future Agent Integration Interface | AI coding agents and orchestration tools | Work packets, review reports, evidence obligations, stage-aware prompts | REQ-006, NFR-005 | Agents need bounded context, not raw repository access alone. | Future ADR if remote orchestration is introduced | Planned |

## Command Contract Rules

- Commands that generate downstream artifacts must refuse to run when their upstream stage gate fails unless an explicit `--force` exists.
- Forced generation must communicate bypass risk and avoid hiding incomplete upstream truth.
- Commands must preserve hand-authored sections unless the task explicitly says otherwise.
- Commands must append durable log entries when they materially change lifecycle artifacts.
- Commands must return non-zero status for blocked gates or invalid inputs.

## API Style Decisions

| Decision | Choice | Rationale | Alternatives | Rollback |
| --- | --- | --- | --- | --- |
| Product-owner automation | CLI-first | Works locally, fits agent sessions, and keeps outputs auditable. | Hosted API, background service | Keep command logic pure so a future API can wrap it. |
| Cockpit integration | Local bridge over CLI and Python modules | Avoids duplicated business logic in UI. | Separate backend service | Disable cockpit command exposure without breaking CLI. |
| Agent handoff | Files and generated reports | Agents can read stable artifacts without privileged API access. | Direct tool calls only | Continue supporting work-packet files as source of truth. |

## Public API Boundary

No public API is part of the current architecture. A public or remote orchestration API requires:

- an ADR;
- authentication and authorization model;
- audit log model;
- deployment and rollback plan;
- operations runbook;
- explicit product requirement or customer evidence.
