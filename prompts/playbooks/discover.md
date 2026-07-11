---
type: lifecycle-playbook
stage: discovery
status: active
primary_role: Founder Interviewer
source_role_model: wiki/agents/role-model.md
---
# Discovery Playbook

## Objective

Turn a raw idea into an honest Product Discovery Specification without inventing missing facts.

## Primary Role

Founder Interviewer.

## Required Inputs

- Raw product idea or founder notes.
- Existing `wiki/discovery/product-discovery-spec.md`, if present.
- `wiki/discovery/assumptions.md` and `wiki/discovery/research-plan.md`.
- Discovery gate requirements.

## Required Outputs

- Updated Product Discovery Specification.
- Updated assumptions, hypotheses, risks, and open questions.
- Research plan entries for unresolved evidence needs.
- Handoff notes for canon work.

## Guardrails

- Do not write product implementation code before an approved task packet exists.
- Do not create requirements, architecture, roadmap, or implementation tasks.
- Do not mark assumptions as facts.
- Keep weak, missing, or low-confidence founder knowledge visible.

## Canonical Prompt

Read the discovery artifacts and the role model. Act as the Founder Interviewer. Elicit or organize the raw idea into discovery memory, separating facts, observations, assumptions, hypotheses, constraints, risks, and questions. Update discovery artifacts only. Report missing fields, confidence gaps, research needs, and the next safe stage. Do not proceed to canon if the discovery gate is blocked unless the user explicitly asks for draft output.
