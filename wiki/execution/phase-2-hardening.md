---
type: execution-phase
stage: execution-planning
phase: phase-2-hardening
status: draft
owner: delivery-planning
updated: 2026-07-10
---
# Phase 2 - Hardening

## Purpose

Phase 2 hardens the execution system around agent orchestration, handoffs, graph expansion, statement confidence, and traceability. It turns a runnable baseline into a safer AI-native delivery system.

## Source Inputs

- Roadmap: [[../roadmap/architecture-roadmap]], [[../roadmap/engineering-roadmap]]
- Architecture: [[../architecture/component-architecture]], [[../architecture/context-map]], [[../architecture/observability-architecture]]
- Requirements: [[../requirements/product-requirements]], [[../requirements/non-functional-requirements]]

## Phase Objective

Make AI-agent collaboration traceable, role-bounded, and graph-backed before validation and release work expands.

## Scope

- AI agent role model.
- Canonical lifecycle playbooks.
- Agent handoff protocol.
- Expanded graph node types.
- Statement type and confidence on graph nodes.
- Traceability matrix.

## Out Of Scope

- Production release certification.
- Deployment assets.
- Operations runbooks.
- Cockpit lifecycle redesign implementation beyond planning inputs.

## Dependencies

- Phase 1 repository factory baseline.
- TASK-0026 through TASK-0031.
- Existing graph validation remains passing.

## Phase Task List

| Phase Task ID | Task | Objective | Business Reason | Scope | Dependencies | Acceptance Criteria | Tests Required | Validation Command | Documentation Updates | Expected Repo Changes | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EP2-001 | Define AI agent role model | Describe delivery-team roles, responsibilities, inputs, outputs, and forbidden actions. | Agents need bounded responsibilities to avoid uncontrolled implementation. | Founder Interviewer through Governance Auditor roles. | TASK-0026 | Every role has responsibilities, inputs, outputs, and forbidden actions. | Documentation review | `make wiki-health` | Add role model docs. | New role/playbook docs. | Planned |
| EP2-002 | Add lifecycle playbooks and handoff protocol | Replace duplicated prompt packs with canonical stage playbooks and handoff summaries. | Handoffs should preserve assumptions, risks, unresolved questions, and next-stage instructions. | Playbooks for lifecycle stages and handoff protocol. | EP2-001, TASK-0027, TASK-0028 | Tool-specific prompts can render from canonical playbooks; handoffs include required fields. | Documentation and prompt review | `make wiki-health` | Add `prompts/playbooks/*.md` and handoff docs. | Prompt/playbook files. | Planned |
| EP2-003 | Expand graph lifecycle coverage | Add lifecycle node types and graph metadata for statement type, confidence, source stage, and verification status. | AI must distinguish facts from assumptions and trace lifecycle chains. | Discovery, assumption, strategy, domain, architecture, test, deployment, operations, contradiction, and learning nodes. | TASK-0029, TASK-0030 | Graph validation passes and nodes carry required metadata where available. | Unit and graph tests | `python3 tools/echel.py graph validate` | Update graph docs and traceability docs. | Graph code/tests/schema updates. | Planned |
| EP2-004 | Generate traceability matrix | Produce a report from discovery through evidence and release. | Owners need impact analysis and broken-chain visibility. | `python3 tools/echel.py traceability` and report artifact. | EP2-003, TASK-0031 | Matrix shows discovery -> canon -> strategy -> requirement -> domain -> architecture -> task -> test -> evidence and highlights broken chains. | Unit tests and report review | `python3 -m unittest discover -s tests` | Add report docs and command docs. | Traceability command and report. | Planned |

## Definition Of Done

- AI roles and handoff protocol are explicit.
- Lifecycle playbooks are canonical rather than duplicated per tool.
- Graph and traceability upgrades preserve existing graph validation.
- Traceability matrix reports broken chains without hiding uncertainty.

## Validation Method

Run:

```bash
make wiki-health
python3 tools/echel.py graph validate
python3 -m unittest discover -s tests
```

## Expected Repository Changes

- New role, playbook, handoff, graph, and traceability docs.
- Graph tooling and tests for expanded lifecycle nodes.
- Traceability report generation under `wiki/reports/`.

## Handoff To Phase 3

Phase 3 may start once agent roles, handoffs, graph metadata, and traceability reporting make validation and release evidence auditable.
