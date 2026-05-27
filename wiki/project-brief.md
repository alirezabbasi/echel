---
type: project-brief
status: active
---
# Project Brief

Echel is a platform for AI-native software development through advanced vibe coding workflows guided by domain experts and AI agents.

It exists to let a business owner, product expert, or domain expert guide product creation by defining requirements, clarifying intent, and steering the vision while Echel and AI agents handle structured execution, software development workflow, and continuity across sessions.

Echel supports both greenfield builds and existing-codebase evolution.

## Operating model
- Domain experts provide intent, requirements, product constraints, and direction.
- AI agents translate that intent into structured tasks, implementation work, verification, and durable project knowledge.
- Echel maintains the persistent memory, orchestration, and governance layer that keeps work coherent over time.
- Humans review outcomes and make final product and business decisions.

## Core promise
Echel continuously accumulates project intelligence so software development can keep moving forward coherently instead of resetting whenever an AI context window resets.

The accumulated intelligence includes:

- operational and architectural knowledge generated during development
- relationships between product, code, decisions, tasks, and standards
- future planning and design direction
- evolving context required for long-term continuity

## Knowledge Boundaries

- `wiki/` is the long-term knowledge layer: canonical concepts, architecture, decisions, relationships, plans, and durable project memory.
- `docs/development/` is the operating layer: SDLC method, execution controls, gates, evidence, automation, memory snapshots, and active process state.

These layers should reference each other without duplicating ownership. When the same idea appears in both places, the wiki should hold durable meaning and relationships while development docs should hold operational procedure.

## Initialization Boundary

In generated target projects:

- `wiki/` stays at the project repository root because it belongs to the product being built.
- `echel-core/` contains the Echel framework, including `docs/development`, tools, prompts, schemas, rules, and automation.
- `echel-core/project.echel` points `WIKI_ROOT` to `../wiki` so Echel can run from the framework folder while updating product-owned memory.
