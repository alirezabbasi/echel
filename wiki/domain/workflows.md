---
type: domain-workflows
stage: domain
status: draft
owner: product
updated: 2026-07-02
---

# Domain Workflows

## Purpose

Domain workflows describe business progress through product memory and lifecycle readiness. They do not describe implementation sequence, user interface behavior, or deployment steps.

## Workflow Register

| ID | Workflow | Objective | Source IDs | Participating Contexts | Status |
| --- | --- | --- | --- | --- | --- |
| WF-DM-001 | Requirement To Domain Concept Mapping | Ensure each requirement has at least one domain concept before architecture. | REQ-001, REQ-002, REQ-004 | BC-001, BC-002, BC-004 | Draft |
| WF-DM-002 | Scope Boundary Review | Confirm MVP, later, and out-of-scope distinctions before downstream work. | REQ-002 | BC-002, BC-005 | Draft |
| WF-DM-003 | Dependency And Risk Review | Confirm every requirement exposes planning dependencies and risks. | REQ-003, REQ-004 | BC-003, BC-004 | Draft |
| WF-DM-004 | Acceptance Readiness Review | Confirm every MVP requirement has acceptance and verification. | REQ-004, REQ-005, NFR-003 | BC-004, BC-005 | Draft |
| WF-DM-005 | Agent Handoff Preparation | Package domain concepts and requirement fields for future execution planning. | REQ-006, NFR-005 | BC-005 | Draft |

## Workflow Steps

| Workflow ID | Step | Actor Role | Input | Output | Completion Signal |
| --- | --- | --- | --- | --- | --- |
| WF-DM-001 | 1 | Domain Modeler | Gated requirements | Candidate `DM-###` concepts | Concept rows added. |
| WF-DM-001 | 2 | Product Manager | Candidate concepts | Requirement coverage table | Every requirement marked covered. |
| WF-DM-002 | 1 | Product Manager | MVP scope and out-of-scope records | Scope boundary review | No requirement is unclassified. |
| WF-DM-003 | 1 | Domain Modeler | Requirement dependency and risk fields | Planning readiness concepts | Dependency and risk concepts mapped. |
| WF-DM-004 | 1 | QA Agent | Acceptance criteria and verification methods | Validation contract concepts | Every MVP requirement has proof path. |
| WF-DM-005 | 1 | Delivery Planner | Covered requirements and domain concepts | Handoff-ready domain summary | Future `echel domain` can add graph nodes. |

## Workflow Open Questions

| ID | Question | Source IDs | Owner | Status |
| --- | --- | --- | --- | --- |
| Q-DM-002 | Should domain workflows include generated `REQ-101+` rows once real strategy content is available? | REQ-006, NFR-005 | Product | Open |

