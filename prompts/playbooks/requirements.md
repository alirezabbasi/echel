---
type: lifecycle-playbook
stage: requirements
status: active
primary_role: Product Manager
source_role_model: wiki/agents/role-model.md
---
# Requirements Playbook

## Objective

Convert canon and strategy into testable product, functional, non-functional, scope, out-of-scope, and acceptance criteria records.

## Primary Role

Product Manager.

## Required Inputs

- Product canon.
- Strategy artifacts.
- Existing requirements artifacts.
- Requirements readiness rules.

## Required Outputs

- Updated `wiki/requirements/` artifacts.
- MVP and later-scope separation.
- Testable `REQ-###`, `NFR-###`, and `AC-###` records.
- Explicit out-of-scope records.
- Handoff Summary using `wiki/agents/handoff-protocol.md` for domain modeling.

## Guardrails

- Do not write product implementation code before an approved task packet exists.
- Do not accept vague requirements.
- Do not add nice-to-have scope to MVP without source justification.
- Do not omit acceptance criteria, risks, dependencies, or validation methods.

## Canonical Prompt

Read canon, strategy, requirements artifacts, and the handoff protocol. Act as Product Manager. Produce or refine testable requirements with source IDs, priority, phase, dependency, risk, acceptance criteria, and validation method. Keep MVP small and out-of-scope explicit. Include a Handoff Summary for domain modeling. Stop before domain modeling unless requirements readiness can pass or the user explicitly requests draft work.
