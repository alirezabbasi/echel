---
type: architecture-context-map
stage: architecture
status: draft
owner: architecture
updated: 2026-07-02
---
# Context Map

## Purpose

The context map translates domain bounded contexts into architecture boundaries while preserving each context's responsibility and forbidden responsibilities.

## Domain To Architecture Contexts

| Domain Context | Architecture Context | Responsibility | Preserved Boundary | Source IDs | Status |
| --- | --- | --- | --- | --- | --- |
| BC-001 Product Memory Governance | ARCH-101 Product Memory Context | Own product wiki artifacts, stable IDs, source links, and generated sections. | Does not decide delivery scope or architecture by itself. | REQ-001, REQ-005, NFR-001, NFR-002 | Draft |
| BC-002 Scope Control | ARCH-102 Scope Planning Context | Preserve MVP, later, and excluded scope for roadmap and task generation. | Does not define acceptance evidence. | REQ-002 | Draft |
| BC-003 Planning Readiness | ARCH-103 Readiness Context | Surface dependencies, risks, gate failures, and remediation messages. | Does not resolve risks without owner decision. | REQ-003, REQ-004 | Draft |
| BC-004 Validation Contract | ARCH-104 Validation Context | Preserve acceptance criteria, verification methods, and evidence expectations. | Does not implement tests or architecture. | REQ-004, REQ-005, NFR-003 | Draft |
| BC-005 Agent Handoff | ARCH-105 Agent Handoff Context | Package approved product, domain, architecture, and acceptance context for AI agents. | Does not create implementation tasks before architecture and planning are ready. | REQ-006, NFR-005 | Draft |

## Generated Domain Context Coverage

| Source Context Pattern | Architecture Handling | Rationale | Status |
| --- | --- | --- | --- |
| BC-2xx generated requirement contexts | Map to the nearest ARCH-10x context based on requirement intent. | Generated domain rows preserve requirement coverage; architecture should consolidate boundaries only when responsibilities match. | Draft |
| Quality contexts from NFR-### | Map to validation, security, observability, or data architecture as appropriate. | NFRs should shape architecture qualities without becoming separate services by default. | Draft |
| Agent consumption context | Map to work-packet, prompt, cockpit, and command surfaces. | Agent handoff needs structured context and verification obligations. | Draft |

## Integration Boundaries

| From Context | Interaction | To Context | Contract | Rationale |
| --- | --- | --- | --- | --- |
| ARCH-101 Product Memory Context | supplies source artifacts to | ARCH-103 Readiness Context | Markdown files and graph manual nodes | Gates must evaluate committed product memory. |
| ARCH-103 Readiness Context | blocks or permits | ARCH-105 Agent Handoff Context | Gate result and remediation list | Agents must not receive unsafe work. |
| ARCH-104 Validation Context | supplies evidence expectations to | ARCH-105 Agent Handoff Context | Acceptance criteria and verification methods | Work packets need proof obligations. |
| ARCH-102 Scope Planning Context | constrains | ARCH-105 Agent Handoff Context | MVP and out-of-scope records | Agents must not implement later-scope items early. |
| ARCH-101 Product Memory Context | feeds | ARCH-201 Product Graph Component | Wiki pages and manual graph data | Graph connects product memory into traversable context. |

## Boundary Rules

- Architecture contexts may group multiple domain contexts only when no forbidden responsibility is violated.
- A component must not own a domain term unless that term is defined in [[../domain/ubiquitous-language]].
- A roadmap phase must cite the architecture context it changes.
- A future architecture gate must block components that ignore bounded-context ownership.
