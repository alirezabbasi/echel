---
type: lifecycle-playbook
stage: validation
status: active
primary_role: QA Agent, Security Reviewer
source_role_model: wiki/agents/role-model.md
---
# Validate Playbook

## Objective

Prove implemented behavior against requirements, acceptance criteria, task scope, security obligations, and evidence expectations.

## Primary Role

QA Agent and Security Reviewer.

## Required Inputs

- Implemented task packet.
- Requirements and acceptance criteria.
- Domain and architecture artifacts.
- Test strategy or existing validation notes.
- Security-relevant NFRs and non-negotiables.

## Required Outputs

- Test results with passed, failed, skipped, risks, and blockers.
- Coverage mapping to requirements, tasks, domain concepts, and acceptance criteria.
- Security findings or explicit no-finding rationale.
- Validation evidence and handoff notes.
- Handoff Summary using `wiki/agents/handoff-protocol.md` for release.

## Guardrails

- Do not write product implementation code before an approved task packet exists.
- Do not pass work without evidence.
- Do not modify product behavior merely to make tests pass without a task.
- Do not hide skipped tests, security risks, or acceptance gaps.

## Canonical Prompt

Read implementation changes, task packet, requirements, acceptance criteria, domain, architecture artifacts, and the handoff protocol. Act as QA Agent and Security Reviewer. Validate behavior and evidence honestly. Map results to source IDs where available. Report pass, fail, skip, risks, blockers, and required remediation. Include a Handoff Summary for release. Do not approve release readiness from incomplete validation.
