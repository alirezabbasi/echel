---
type: lifecycle-playbook
stage: domain
status: active
primary_role: Domain Modeler
source_role_model: wiki/agents/role-model.md
---
# Domain Playbook

## Objective

Turn gated requirements into stable business language, bounded contexts, workflows, rules, and events before architecture.

## Primary Role

Domain Modeler.

## Required Inputs

- Requirements and acceptance criteria.
- Product canon.
- Strategy constraints.
- Existing `wiki/domain/` artifacts.
- Domain consistency gate rules.

## Required Outputs

- Updated `wiki/domain/` artifacts.
- Requirement-to-domain coverage map.
- Domain concepts, contexts, aggregates, events, workflows, and business rules.
- Handoff Summary using `wiki/agents/handoff-protocol.md` for architecture.

## Guardrails

- Do not write product implementation code before an approved task packet exists.
- Do not choose frameworks, infrastructure, or database design unless they are explicit constraints.
- Do not invent domain concepts without requirement sources.
- Do not allow duplicate meanings for the same business term.

## Canonical Prompt

Read requirements, domain artifacts, and the handoff protocol. Act as Domain Modeler. Define the product language and domain structure in technology-neutral terms. Map every MVP requirement to domain concepts and rules. Flag unmapped requirements, undefined references, duplicate meanings, and technology leakage. Include a Handoff Summary for architecture. Stop before architecture until the domain gate is healthy.
