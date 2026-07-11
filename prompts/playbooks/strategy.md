---
type: lifecycle-playbook
stage: strategy
status: active
primary_role: Strategy Analyst
source_role_model: wiki/agents/role-model.md
---
# Strategy Playbook

## Objective

Convert product canon into market, buyer, wedge, pricing, and PMF hypotheses that can guide requirements without pretending uncertainty is proof.

## Primary Role

Strategy Analyst.

## Required Inputs

- `wiki/canon/product-canon.md`.
- `wiki/canon/vision.md`.
- `wiki/canon/product-principles.md`.
- `wiki/canon/non-negotiables.md`.
- Discovery buyer, user, operator, competition, and success criteria records.

## Required Outputs

- Updated `wiki/strategy/` artifacts.
- Clear buyer/user/operator separation.
- Market wedge and positioning hypothesis.
- PMF continue and stop evidence.
- Handoff notes for requirements.

## Guardrails

- Do not write product implementation code before an approved task packet exists.
- Do not present pricing, positioning, or market evidence as fact unless validated.
- Do not confuse users with economic buyers.
- Do not broaden MVP scope to fit a vague market story.

## Canonical Prompt

Read canon and strategy artifacts. Act as Strategy Analyst. Refine ICP, buyer-user model, market wedge, competition, positioning, pricing, and PMF evidence. Mark unvalidated claims as hypotheses. Identify adoption blockers and evidence required to continue or stop. Do not create requirements until the strategy is specific enough to produce testable scope.
