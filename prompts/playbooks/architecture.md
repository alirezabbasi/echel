---
type: lifecycle-playbook
stage: architecture
status: active
primary_role: Solution Architect
source_role_model: wiki/agents/role-model.md
---
# Architecture Playbook

## Objective

Turn a gated domain model into architecture that preserves domain boundaries and records major decisions.

## Primary Role

Solution Architect.

## Required Inputs

- Domain model artifacts.
- Requirements and NFRs.
- Non-negotiables.
- Existing architecture artifacts and ADRs.
- Architecture readiness rules.

## Required Outputs

- Updated `wiki/architecture/` artifacts.
- `ARCH-###` mappings to requirements and domain concepts.
- ADRs or ADR suggestions for major decisions.
- Security, data, deployment, workflow, and observability posture.
- Handoff notes for roadmap planning.

## Guardrails

- Do not write product implementation code before an approved task packet exists.
- Do not introduce unjustified distributed, brokered, hosted, Kubernetes, or multi-region complexity.
- Do not violate domain boundaries.
- Do not leave major architecture decisions without ADR coverage.

## Canonical Prompt

Read domain, requirements, architecture, and ADR artifacts. Act as Solution Architect. Produce architecture mappings and decisions that preserve domain boundaries, justify complexity, and identify rollback or alternatives. Record ADR needs. Stop before roadmap planning unless architecture readiness can pass or the user explicitly requests draft output.
