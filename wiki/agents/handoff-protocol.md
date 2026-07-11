---
type: agent-handoff-protocol
stage: orchestration
status: active
owner: governance
updated: 2026-07-11
---
# Agent Handoff Protocol

## Purpose

This protocol defines how one Echel AI role hands work to the next role without losing assumptions, risks, unresolved questions, evidence, or next-stage instructions.

It complements [[role-model]] and `prompts/playbooks/`. The role model defines who is responsible. The playbooks define how each role acts. This protocol defines what every role must leave behind.

## Applicability

Every lifecycle stage output must include a Handoff Summary when it creates, changes, validates, releases, operates, or governs product memory.

This applies to:

- Discovery to Canon
- Canon to Strategy
- Strategy to Requirements
- Requirements to Domain
- Domain to Architecture
- Architecture to Roadmap
- Roadmap to Execution
- Execution to Validation
- Validation to Release
- Release to Operations
- Operations to Governance or Evolution
- Governance back to any affected stage

## Required Handoff Summary

Use this structure in stage outputs, task summaries, review reports, release notes, operational notes, and governance reports.

```text
## Handoff Summary

From role:
To role:
Lifecycle stage:
Source artifacts:
Changed artifacts:
Decision summary:
Assumptions:
Risks:
Unresolved questions:
Evidence and verification:
Stale or impacted upstream artifacts:
Next-stage instructions:
Do not proceed if:
```

## Field Rules

| Field | Requirement |
| --- | --- |
| From role | Must name one role from [[role-model]]. |
| To role | Must name the next responsible role or `Product Owner` when human clarification is needed. |
| Lifecycle stage | Must match the stage being handed off. |
| Source artifacts | Must list the product-memory artifacts read or generated. |
| Changed artifacts | Must list documents, code, tests, reports, or generated outputs changed. |
| Decision summary | Must summarize decisions made or state `No new decision`. |
| Assumptions | Must list assumptions by ID where available, or state `None`. |
| Risks | Must list risks by ID where available, or state `None`. |
| Unresolved questions | Must list open questions by ID where available, or state `None`. |
| Evidence and verification | Must list commands, reports, proof, or evidence records, or state why none exists. |
| Stale or impacted upstream artifacts | Must name upstream artifacts that need refresh, or state `None`. |
| Next-stage instructions | Must tell the receiving role what to read, what to verify, and what not to do. |
| Do not proceed if | Must state the blocking condition that stops the next role. |

## Stage Routing

| From Stage | From Role | To Stage | To Role | Required Handoff Focus |
| --- | --- | --- | --- | --- |
| Discovery | Founder Interviewer | Canon | Business Analyst, Product Manager | Facts, assumptions, open questions, research gaps. |
| Canon | Business Analyst, Product Manager | Strategy | Strategy Analyst | Product truth, non-negotiables, unresolved identity questions. |
| Strategy | Strategy Analyst | Requirements | Product Manager | ICP, buyer/user separation, wedge, pricing and PMF hypotheses. |
| Requirements | Product Manager | Domain | Domain Modeler | Testable scope, acceptance criteria, out-of-scope boundaries. |
| Domain | Domain Modeler | Architecture | Solution Architect | Domain concepts, bounded contexts, workflows, rules, unmapped terms. |
| Architecture | Solution Architect | Roadmap | Delivery Planner | Architecture decisions, ADR needs, complexity risks, readiness state. |
| Roadmap | Delivery Planner | Execution | Delivery Planner | Phase rows, dependencies, validation commands, task generation inputs. |
| Execution | Implementation Agent | Validation | QA Agent, Security Reviewer | Modified files, proof, tests, evidence, scope risks. |
| Validation | QA Agent, Security Reviewer | Release | Release Manager | Passed/failed/skipped results, security findings, release blockers. |
| Release | Release Manager | Operations | Operations Steward | Release proof, rollback, accepted risks, monitoring expectations. |
| Operations | Operations Steward | Governance | Governance Auditor | Incidents, metrics, learnings, stale docs, evolution candidates. |
| Governance | Governance Auditor | Affected stage role | Owner of affected stage | Contradictions, integrity failures, exceptions, remediation tasks. |

## Blocking Rules

- Do not hand off implementation work without an approved `wiki/work/TASK-*.md` task packet.
- Do not hand off a stage as complete when required gate checks are blocked.
- Do not hide assumptions, risks, skipped checks, or unresolved questions.
- Do not send downstream roles to stale upstream artifacts without naming the stale state.
- Do not ask a receiving role to exceed its role-model forbidden actions.

## Relationship To Playbooks

Every canonical lifecycle playbook must require a Handoff Summary using this protocol. Tool-specific prompts may format the handoff for their runtime, but they must preserve the required fields.
