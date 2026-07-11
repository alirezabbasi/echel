---
type: playbook-index
stage: orchestration
status: active
owner: governance
updated: 2026-07-11
---
# Canonical Lifecycle Playbooks

These playbooks are the canonical prompt source for Echel lifecycle work. Tool-specific prompt packs under `prompts/codex/`, `prompts/claude-code/`, and `prompts/cursor/` should render from these playbooks instead of duplicating lifecycle instructions.

## Rendering Contract

Tool-specific prompts must preserve these sections from the selected playbook:

- Objective
- Primary role
- Required inputs
- Required outputs
- Handoff Summary
- Guardrails
- Canonical prompt

Tools may add syntax for their runtime, but they must not remove safety requirements, source-of-truth references, validation expectations, or the rule that no implementation code may be written before an approved execution task packet exists.

## Playbooks

| Playbook | Primary role | Stage |
| --- | --- | --- |
| `discover.md` | Founder Interviewer | Discovery |
| `canon.md` | Business Analyst, Product Manager | Canon |
| `strategy.md` | Strategy Analyst | Strategy |
| `requirements.md` | Product Manager | Requirements |
| `domain.md` | Domain Modeler | Domain |
| `architecture.md` | Solution Architect | Architecture |
| `roadmap.md` | Delivery Planner | Roadmap |
| `execute.md` | Implementation Agent | Implementation |
| `validate.md` | QA Agent, Security Reviewer | Validation |
| `release.md` | Release Manager | Release |
| `operate.md` | Operations Steward | Operations |
| `govern.md` | Governance Auditor | Governance |

## Universal Guardrails

- Do not write product implementation code before a generated and approved `wiki/work/TASK-*.md` task packet exists.
- Do not treat assumptions, hypotheses, or low-confidence statements as facts.
- Do not advance a lifecycle stage when its upstream gate is blocked unless the user explicitly asks for draft or forced output.
- Do not silently change source-of-truth hierarchy, architecture decisions, or task scope.
- Record unresolved questions, assumptions, risks, and stale upstream artifacts for handoff.
- Include a Handoff Summary using `wiki/agents/handoff-protocol.md` in every stage output.
