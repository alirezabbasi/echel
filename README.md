# Echel

![Echel Banner](assets/echel.png)

**Echel is a product-creation platform for AI-native software development.**

A domain expert defines a problem, intended solution, constraints, and direction. Echel continuously turns that intent into clarified requirements, product architecture, roadmap, executable work, verified software, and compounding project intelligence.

Echel exists for one simple reason: AI agents are powerful, but their context is temporary. Real products need memory. They need decisions, tradeoffs, architecture, work, evidence, risks, and direction to survive across sessions. Echel gives a software project that persistent intelligence layer.

## What Echel Does

Echel helps a product move from idea to implementation without losing coherence.

- Captures product intent as structured memory.
- Clarifies ambiguity before agents build.
- Turns requirements into roadmap and executable work.
- Turns gated requirements into domain language before architecture.
- Blocks architecture when domain language is incomplete, inconsistent, or technology-leaky.
- Preserves architecture decisions, boundaries, data, APIs, workflows, security, and observability as product memory.
- Builds a typed product intelligence graph.
- Generates graph-backed work packets for AI coding agents.
- Reviews work against acceptance criteria and evidence expectations.
- Tracks risks, decisions, contradictions, and architecture.
- Certifies milestone and release readiness with proof packs.
- Gives product owners a local cockpit for steering the product.

## The Core Idea

Most AI coding workflows happen inside conversations. Those conversations disappear, overflow, or reset. Echel moves the important intelligence out of chat and into a living project memory.

The product itself accumulates:

- what is being built
- why it matters
- who it serves
- what has been decided
- what remains uncertain
- how the architecture is evolving
- what work is planned or complete
- what evidence proves progress
- what risks still block release

That memory compounds over time, so each new AI session starts from the project’s actual state instead of a fading summary.

## Product-First Workflow

Echel starts with the product, not the framework.

The first experience asks about:

- problem
- users
- intended solution
- MVP
- constraints
- risks
- preferred stack
- success criteria
- product direction

From there, Echel creates a root-level `wiki/` that belongs to the product. The framework runtime lives separately in `echel-core/`, where it can operate without cluttering the product repository.

## Product Intelligence Graph

Echel stores product memory in Markdown so humans and AI agents can read it, but the real leverage comes from the typed graph underneath.

The graph connects:

- problems
- users and needs
- requirements
- features
- workflows
- components
- decisions
- risks
- tasks
- evidence
- milestones and releases

This lets Echel reason across the product instead of treating every task as an isolated file.

## Agent Work Packets

Before an AI agent writes code, Echel can prepare a graph-backed build packet.

Each packet includes:

- objective
- product context
- graph context
- likely files
- constraints
- acceptance criteria
- verification commands
- evidence obligations
- required memory updates

The goal is to give agents enough structured context to implement the right thing, not merely produce code that looks plausible.

## Product Cockpit

Echel includes a local cockpit for steering product creation.

The cockpit brings together:

- product direction
- clarification queue
- roadmap
- current work
- architecture
- product graph
- build packets
- review reports
- readiness
- risks
- contradictions
- agent activity
- decisions
- chat

Chat remains useful, but it is no longer the whole product experience.

## Readiness And Proof Packs

Echel gates progress in product language:

- idea clarified
- MVP scoped
- feature ready
- feature verified
- release candidate
- production ready

Readiness reports and proof packs show what is ready, what is blocked, what evidence exists, and what should happen next.

## Why It Matters

Echel is designed for founders, business owners, domain experts, and AI-assisted engineering teams who want to build real software products with AI agents without losing the thread.

The promise is not “AI writes code.”

The promise is:

> A product can continuously understand, organize, verify, and evolve itself as it is being built.

## Learn More

- [Technical Quick Start](docs/technical-quick-start.md)
- [Operational Method](docs/development/method.md)
- [Product Graph](docs/development/phase2-product-graph.md)
- [Agent Work Packets](docs/development/phase3-agent-work-packets.md)
- [Product Cockpit](docs/development/phase4-product-cockpit.md)
- [Readiness And Proof Packs](docs/development/phase5-readiness-and-proof-packs.md)
- [V2 Product Direction Review](wiki/reports/echel-v2-product-direction-review.md)

## Quick Start

```bash
make init-wizard
```

Then:

```bash
cd <project-name>/echel-core
make wiki-health
python3 tools/echel.py status
```

Full setup and command details live in the [Technical Quick Start](docs/technical-quick-start.md).
