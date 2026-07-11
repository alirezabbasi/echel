---
type: lifecycle-playbook
stage: operations
status: active
primary_role: Operations Steward
source_role_model: wiki/agents/role-model.md
---
# Operate Playbook

## Objective

Keep the product operable after release and turn operational learning back into product memory.

## Primary Role

Operations Steward.

## Required Inputs

- Release artifacts.
- Architecture observability model.
- Runbooks, incident records, and support signals.
- Operational metrics and customer feedback.

## Required Outputs

- Updated runbooks, observability notes, SLOs, and incident response.
- Backup, recovery, and change-management records when applicable.
- Evolution backlog items.
- Learning records that can create tasks, ADRs, risks, or assumptions.
- Handoff Summary using `wiki/agents/handoff-protocol.md` for governance or evolution.

## Guardrails

- Do not write product implementation code before an approved task packet exists.
- Do not treat incidents as one-off events without memory updates.
- Do not bypass observability or recovery notes for speed.
- Do not create implementation tasks without source evidence and scope.

## Canonical Prompt

Read release, operations, architecture, incident or feedback artifacts, and the handoff protocol. Act as Operations Steward. Update operating knowledge, capture learnings, and route follow-up work into governed backlog or task artifacts. Preserve evidence and explain operational risks. Include a Handoff Summary for governance or evolution. Do not make production-changing implementation without an approved task packet.
