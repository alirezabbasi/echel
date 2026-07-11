---
type: lifecycle-playbook
stage: implementation
status: active
primary_role: Implementation Agent
source_role_model: wiki/agents/role-model.md
---
# Execute Playbook

## Objective

Implement exactly one approved execution task packet and return proof, tests, and synchronized memory.

## Primary Role

Implementation Agent.

## Required Inputs

- One selected `wiki/work/TASK-*.md` task packet.
- Product canon.
- Relevant requirements, domain, architecture, and ADR artifacts.
- `wiki/engineering/development-workflow.md`.
- Validation command named by the task packet.

## Required Outputs

- Scoped source changes.
- Tests or justified test exception.
- Runnable proof and validation command results.
- Updated project memory and implementation handoff.
- Notes for stale upstream artifacts or follow-up work.

## Guardrails

- Do not write product implementation code before an approved task packet exists.
- Do not implement from raw idea, chat-only instruction, roadmap prose, or phase prose.
- Do not modify unrelated files.
- Do not change architecture while implementing unless the task explicitly asks for it.
- Do not close the task without proof, tests or test exception, and memory updates.

## Canonical Prompt

Read the selected task packet and linked product memory. Act as Implementation Agent. Before editing, identify the exact files likely to change and the verification command. Implement only the requested scope. Preserve unrelated work. Add or update tests. Run the task validation. Update relevant memory and summarize modified files, proof, tests, risks, and follow-up items. Do not proceed to any other task.
