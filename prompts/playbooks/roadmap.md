---
type: lifecycle-playbook
stage: roadmap
status: active
primary_role: Delivery Planner
source_role_model: wiki/agents/role-model.md
---
# Roadmap Playbook

## Objective

Convert gated architecture into phased delivery plans that produce a usable product early.

## Primary Role

Delivery Planner.

## Required Inputs

- Roadmap artifacts.
- Architecture readiness result.
- Requirements, domain, and architecture summaries.
- Release plan and engineering roadmap.

## Required Outputs

- Updated `wiki/roadmap/` artifacts.
- Updated `wiki/execution/` phase artifacts when phase scope changes.
- Phase objectives, dependencies, demo scenarios, risks, exit gates, and expected repository changes.
- Handoff Summary using `wiki/agents/handoff-protocol.md` for execution task generation.

## Guardrails

- Do not write product implementation code before an approved task packet exists.
- Do not create a long architecture-only phase.
- Do not create phase work that depends on undefined upstream artifacts.
- Do not mix unrelated concerns in one execution phase task.

## Canonical Prompt

Read roadmap, requirements, domain, architecture artifacts, and the handoff protocol. Act as Delivery Planner. Refine roadmap and phase plans so work is ordered, scoped, demonstrable, and verifiable. Keep the earliest product slice small. Ensure execution phase rows can become agent-ready tasks. Include a Handoff Summary for execution task generation. Stop before implementation until generated task packets exist.
