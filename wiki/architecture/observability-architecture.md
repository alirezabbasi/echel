---
type: observability-architecture
stage: architecture
status: draft
owner: architecture
updated: 2026-07-02
---
# Observability Architecture

## Purpose

Observability architecture defines how Echel exposes product state, lifecycle progress, gate results, verification evidence, graph health, and operational issues.

## Observable Surfaces

| ID | Surface | Signal | Producer | Consumer | Source IDs | Status |
| --- | --- | --- | --- | --- | --- | --- |
| ARCH-801 | Lifecycle Log | Durable lifecycle changes and command effects | Lifecycle commands and manual updates | Product owner, governance auditor | REQ-001, NFR-002 | Existing |
| ARCH-802 | Doctor Report | Primitive, evidence, drift, and gate status | `echel doctor` | Product owner, agent, CI candidate | REQ-003, REQ-004, NFR-003 | Existing |
| ARCH-803 | Stage Readiness Output | PASS or BLOCKED with remediation messages | Gate engine | Downstream commands and cockpit | REQ-003, NFR-003 | Existing |
| ARCH-804 | Wiki Health Report | Wiki lint, index, and governance validation | `make wiki-health` | Product owner, agent | NFR-001, NFR-004 | Existing |
| ARCH-805 | Product Graph Report | Node and edge summary plus validation issues | Graph tooling | Work packets, cockpit, planning | REQ-001, NFR-002 | Existing |
| ARCH-806 | Proof Packs | Release and milestone evidence summary | Readiness tooling | Release manager, governance auditor | REQ-004, NFR-003 | Existing |
| ARCH-807 | Review Reports | Task outcome and acceptance review | Review tooling | QA agent, product owner | REQ-004, REQ-006 | Existing |

## Observability Decisions

| Decision | Choice | Rationale | Alternatives | Status |
| --- | --- | --- | --- | --- |
| Progress visibility | File-backed reports and command output | Works locally and can be committed or shared. | Hosted telemetry dashboard | Existing |
| Gate visibility | Failures include remediation text | Blocks are useful only when the owner knows what to fix. | Boolean-only gate result | Existing |
| Evidence visibility | Evidence registry and proof packs | Release confidence requires durable verification references. | Chat summaries | Existing |
| Architecture visibility | Concern-specific architecture docs | Future gates can inspect architecture completeness directly. | Single summary page | New |

## Health Checks

| Check | Command | Expected Result | Blocks |
| --- | --- | --- | --- |
| Wiki health | `make wiki-health` | 0 wiki lint or governance issues | Documentation synchronization |
| Graph integrity | `python3 tools/echel.py graph validate` | Product graph validation passed | Work packet context and cockpit graph use |
| Requirements readiness | `python3 tools/echel.py readiness --stage requirements` | `GATE-REQUIREMENTS: PASS` | Domain generation |
| Domain readiness | `python3 tools/echel.py readiness --stage domain` | `GATE-DOMAIN: PASS` | Architecture work |
| Doctor | `python3 tools/echel.py doctor` | All applicable gates pass or known upstream gaps are documented | Release confidence |

## Future Metrics

| Metric | Why It Matters | Owner |
| --- | --- | --- |
| Gate pass rate by stage | Shows where product memory is weak. | Governance Auditor |
| Work packet rework rate | Shows whether agent context is sufficient. | Delivery Planner |
| Evidence coverage by requirement | Shows release readiness quality. | QA Agent |
| Architecture decision coverage | Shows whether major choices have ADRs. | Solution Architect |
