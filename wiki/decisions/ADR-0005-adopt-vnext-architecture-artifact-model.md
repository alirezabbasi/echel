---
type: adr
status: accepted
---
# ADR-0005 - Adopt vNext Architecture Artifact Model

## Decision

Use `wiki/architecture/` as the vNext architecture artifact surface with separate documents for overview, context map, component architecture, data architecture, API architecture, event architecture, workflow architecture, security architecture, and observability architecture.

The root `wiki/architecture.md` remains a thin compatibility page for existing graph and cockpit tooling until downstream commands read the expanded architecture model directly.

## Context

TASK-0018 follows the completed domain consistency gate. Architecture now needs a durable surface that can preserve domain boundaries, explain major choices, and provide enough structure for roadmap, repository factory, task generation, validation, release, and operations work.

The previous `wiki/architecture.md` page was too thin to carry rationale, alternatives, rollback notes, context boundaries, security expectations, observability expectations, and traceability back to requirements and domain artifacts.

## Impact

- Architecture artifacts are split by concern instead of being compressed into one page.
- Major architecture choices must carry rationale, alternatives, rollback notes, source IDs, and ADR coverage.
- Architecture work must preserve the bounded contexts and domain terms approved by `GATE-DOMAIN`.
- Future `echel architecture` automation should write generated sections into these documents rather than overwriting authored architecture guidance.
- Future architecture gates can evaluate the expanded architecture model deterministically.
