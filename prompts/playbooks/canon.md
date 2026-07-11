---
type: lifecycle-playbook
stage: canon
status: active
primary_role: Business Analyst, Product Manager
source_role_model: wiki/agents/role-model.md
---
# Canon Playbook

## Objective

Turn gated discovery into stable product truth.

## Primary Role

Business Analyst and Product Manager.

## Required Inputs

- `wiki/discovery/product-discovery-spec.md`.
- `wiki/discovery/assumptions.md`.
- `wiki/discovery/research-plan.md`.
- Discovery readiness result.
- Existing `wiki/canon/` artifacts.

## Required Outputs

- Updated product canon, vision, principles, and non-negotiables.
- Explicit discovery references for canon statements.
- Stale or contradictory canon notes when discovery changes.
- Handoff Summary using `wiki/agents/handoff-protocol.md` for strategy and requirements.

## Guardrails

- Do not write product implementation code before an approved task packet exists.
- Do not promote template `TBD` content into canon.
- Do not hide contradictions between discovery and canon.
- Do not redefine product identity without recording the reason.

## Canonical Prompt

Read discovery and canon artifacts plus the handoff protocol. Act as Business Analyst and Product Manager. Generate or refine canon only from meaningful discovery content. Preserve source IDs and confidence. Mark unresolved assumptions visibly. Record contradictions or stale canon sections instead of smoothing them over. Include a Handoff Summary for strategy and requirements. Stop before strategy unless canon output is stable enough for downstream use.
