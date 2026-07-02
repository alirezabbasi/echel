---
type: security-architecture
stage: architecture
status: draft
owner: architecture
updated: 2026-07-02
---
# Security Architecture

## Purpose

Security architecture protects product memory, command execution, local runtime state, evidence, and future agent interactions.

## Trust Boundaries

| ID | Boundary | Assets Protected | Threats | Controls | Source IDs | Status |
| --- | --- | --- | --- | --- | --- | --- |
| ARCH-701 | Repository Boundary | Product wiki, schemas, tools, graph, evidence, decisions | Accidental overwrite, unreviewed generated changes, hidden state | Git review, generated section boundaries, non-destructive edit policy | REQ-001, NFR-002 | Existing |
| ARCH-702 | Command Boundary | CLI commands and lifecycle generators | Unsafe command execution, gate bypass, partial writes | Stage gates, explicit `--force`, non-zero blocked exits | REQ-003, REQ-004, NFR-003 | Existing |
| ARCH-703 | Cockpit Boundary | Local UI, provider config, chat state, command bridge | Unauthorized command execution, secret exposure | Local-first runtime, safe command bridge, provider config isolation | REQ-006, NFR-005 | Existing |
| ARCH-704 | Agent Boundary | Work packets, review outputs, evidence obligations | Agent implements outside scope or ignores architecture | Scoped packets, acceptance criteria, review gate, evidence registry | REQ-004, REQ-006 | Existing |
| ARCH-705 | Future Hosted Boundary | Shared teams, remote orchestration, public APIs | Tenant isolation, auth, audit, network exposure | Requires future ADR, security model, deployment runbook | Future requirement | Planned |

## Security Decisions

| Decision | Choice | Rationale | ADR Coverage | Revisit Trigger |
| --- | --- | --- | --- | --- |
| Product memory storage | Local repository files | Keeps owner control and auditability simple. | ADR-0001, ADR-0004 | Multi-user hosted collaboration becomes a product requirement. |
| Command execution | Local CLI with explicit gates | Avoids hidden automation and makes blocked states visible. | ADR-0002, ADR-0005 | Remote orchestration or scheduled execution is introduced. |
| Secrets | Keep out of product wiki and generated docs | Product memory should be commit-safe. | Future ADR if secret management becomes first-class | Provider and deployment integrations require secrets. |
| Force overrides | Allow only explicit bypass flags on selected commands | Owners may need draft generation, but bypass risk must be visible. | ADR-0005 | Architecture gate requires accepted exceptions model. |

## Security Requirements For Future Tasks

- TASK-0019 must not generate architecture that requires secrets in committed wiki files.
- TASK-0020 should block missing security model and unaccepted hosted-boundary choices.
- Repository factory work must include local development secret handling and ignored environment examples.
- Release work must include deployment security and rollback checks before production readiness.

## Security Traceability

| Requirement Or Domain ID | Security Concern | Architecture Response |
| --- | --- | --- |
| REQ-001 | Preserve intent and source links. | Protect committed memory and stable IDs from silent overwrite. |
| REQ-004 | Link requirements to acceptance criteria. | Require evidence before task closure or release proof. |
| REQ-006 | Agent consumption. | Provide bounded packets and review obligations. |
| NFR-002 | Traceability. | Keep graph, ADRs, logs, and evidence IDs stable. |
| BC-005 | Agent Handoff. | Limit agent context to gated, scoped work. |
