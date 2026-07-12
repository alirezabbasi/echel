---
type: architecture-roadmap
stage: roadmap
status: draft
owner: architecture
updated: 2026-07-10
---
# Architecture Roadmap

## Purpose

The architecture roadmap maps architecture choices into delivery increments. It keeps roadmap planning tied to the architecture gate so execution phases do not invent new components, deployment models, or integration boundaries.

## Source Architecture

- Architecture overview: [[../architecture/overview]]
- Component architecture: [[../architecture/component-architecture]]
- Workflow architecture: [[../architecture/workflow-architecture]]
- Security architecture: [[../architecture/security-architecture]]
- Observability architecture: [[../architecture/observability-architecture]]
- Gate: `python3 tools/echel.py readiness --stage architecture`

## Architecture Delivery Map

| Architecture Item | Roadmap Phase | Objective | Scope | Dependencies | Demo Scenario | Risk | Exit Gate | Source IDs | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARCH-203 Gate Engine | RM-002 Execution Planning MVP | Preserve gate-first execution planning. | Execution phases must cite upstream readiness gates and blocking conditions. | GATE-REQUIREMENTS, GATE-DOMAIN, GATE-ARCHITECTURE | Execution phase document shows exact prerequisite gates. | Phases start from artifact presence instead of readiness. | Every execution phase lists required gates and validation command. | REQ-003, NFR-003, TASK-0022 | Done |
| ARCH-208 Architecture Artifact Surface | RM-002 Execution Planning MVP | Use expanded architecture as execution input. | Phase documents reference architecture context, component, data, API, security, and observability surfaces. | TASK-0018, TASK-0019, TASK-0020 | Phase planning can point to concrete architecture docs. | Architecture is summarized away during planning. | Each phase cites at least one architecture artifact. | ADR-0005, TASK-0022 | Done |
| ARCH-205 Work Packet Generator | RM-003 Agent-Executable Task Layer | Turn roadmap and phase context into small agent work. | Task format includes context, scope, files, acceptance, verification, rollback, docs, out-of-scope. | RM-002, TASK-0023 | One generated task packet is readable without extra conversation. | Agent tasks are too large or vague. | Generated task passes the upgraded task contract. | REQ-006, NFR-005, TASK-0023 | Done |
| ARCH-201 Product Wiki | RM-004 Repository Factory Slice | Preserve product memory when generating repository skeletons. | Generated repo docs and structure must keep product-owned `wiki/` as source of truth. | ADR-0004, TASK-0024, TASK-0025 | Generated repo and engineering docs identify product-owned memory as the source of truth. | Framework files pollute product memory. | `WIKI_ROOT` boundary remains clear and local docs exist. | REQ-001, NFR-001, TASK-0024 | Done |
| ARCH-202 Lifecycle CLI | RM-004 Repository Factory Slice | Keep generated repository actions scriptable. | Local commands for boot, health, tests, lint, and verification are documented. | TASK-0024, TASK-0025 | User runs documented local commands successfully. | Skeleton requires hidden setup. | README and engineering docs include exact commands. | REQ-005, REQ-006, TASK-0025 | Done |
| ARCH-204 Product Graph | RM-005 Orchestration And Traceability | Expand traceability beyond current product/task graph. | Graph nodes for lifecycle artifacts, statement type, confidence, and traceability matrix. | TASK-0029, TASK-0030, TASK-0031 | Traceability report shows discovery through architecture and task/evidence gaps. | Graph remains too shallow for AI orchestration. | Matrix highlights broken chains with actionable IDs. | NFR-002, TASK-0029..TASK-0031 | Done |
| ARCH-206 Review And Evidence Layer | RM-006 Validation Release Operations | Make validation and release evidence durable. | Validation command, evidence registration, release gate, proof and operations docs. | TASK-0032, TASK-0033, TASK-0034, TASK-0036 | Release readiness report shows evidence, blockers, and accepted risks. | Release remains chat-summary based. | Evidence-backed release gate passes or blocks with remediation. | REQ-004, NFR-003, TASK-0032..TASK-0036 | Planned |
| ARCH-207 Local Cockpit | RM-006 Validation Release Operations | Move cockpit toward lifecycle steering. | Lifecycle stage views, guided stage actions, blockers, responsible AI role. | TASK-0039, TASK-0040 | Owner sees current stage, blocker, next action, and role. | Cockpit stays a passive dashboard. | Lifecycle cockpit view exposes safe stage actions. | REQ-006, TASK-0039, TASK-0040 | Done |

## Architecture Guardrails

- Do not add hosted, distributed, or public API architecture from roadmap alone.
- Any phase that changes deployment posture must create or cite a future ADR.
- Any phase that adds persistent state must update data, security, observability, and operations docs.
- Any phase that creates agent autonomy must preserve scoped work packets and evidence obligations.

## Exit Criteria

- [x] Roadmap phases map to architecture components or gates.
- [x] Architecture complexity remains local-first until evidence requires escalation.
- [x] Future execution phases have architecture inputs instead of inventing system shape.
