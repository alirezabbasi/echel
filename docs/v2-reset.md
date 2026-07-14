# Why Echel v2

Echel v2 is an architectural reset in service of Echel's original idea: project knowledge should start small, mature with the product, guide AI-assisted implementation, and retain what the project learns throughout its life.

## Who Echel is for

### Founders and domain experts

Echel helps people who understand a problem express intent without first learning software architecture or completing an exhaustive product template. It asks questions appropriate to the current maturity stage and preserves answers as reviewable product knowledge.

### Product and engineering teams

Echel gives teams continuity between product reasoning and implementation. Requirements, constraints, decisions, work, and evidence remain connected when contributors, models, or agent tools change.

### AI-native developers and agent operators

Echel compiles bounded work context for coding agents and records what was attempted and verified. It complements agent runtimes rather than replacing their model, tool, session, permission, and delegation systems.

### Maintainers, reviewers, and operators

Echel preserves why a system exists, why consequential choices were made, what evidence supported a change, and what production experience later invalidated. Long-term memory is useful only when it remains concise, attributable, and revisable.

## What was learned from v1

V1 demonstrated useful concepts:

- repository-owned product memory;
- a lifecycle from raw idea through operation;
- agent-ready work packets;
- explicit acceptance and verification;
- evidence, contradictions, and learning;
- provider-independent intent.

It also accumulated structural problems:

- future-stage documents were created before the project had knowledge for them;
- the same truth appeared in summary pages, lifecycle pages, graph files, memory records, reports, and compatibility views;
- broad inferred graph relationships created connectivity without reliable meaning;
- manual evidence registration duplicated what execution tools could capture automatically;
- methodology, storage, agent roles, orchestration, UI, and governance evolved as one coupled system;
- users had to understand Echel's internal taxonomy before they could steer their product.

The result was internally elaborate but increasingly distant from the principle of progressive documentation.

## What changed

### From document scaffolding to progressive records

Initialization now stores only the project and raw idea. Knowledge records appear as the project learns. A stage exists in the methodology without requiring an empty folder or document.

### From many sources of truth to one canonical store

Product knowledge, work, runs, evidence, and findings are small Git-owned records under `.echel/`. Search indexes, graph views, dashboards, and reports may be generated later, but they are never authoritative.

### From dense inferred graphs to explicit relationships

A work item receives knowledge only through declared relationships. Missing context is fixed by adding a justified link, not by injecting the whole repository.

### From a rigid pipeline to progressive maturity

The lifecycle remains:

```text
Idea → Problem → Vision → Strategy → Requirements → Domain → Architecture
→ Roadmap → Execution plan → Tasks → Repository → Implementation
→ Validation → Deployment → Operations and evolution
```

Stages indicate what uncertainty the project is reducing. Later implementation or production evidence may revise any earlier stage. Transitions block only on the minimum accepted knowledge required for the next safe decision.

### From an embedded agent platform to runtime adapters

Echel owns methodology, product truth, context compilation, provenance, and verification policy. Hermes is the first runtime adapter and owns multi-LLM execution, sessions, tools, context-window management, and delegation. The adapter boundary prevents Echel from becoming dependent on Hermes internals and permits other runtimes later.

### From conversational learning to approved project learning

Agents may discover contradictions, constraints, and reusable procedures, but those discoveries become durable product truth only through explicit, reviewable records. Runtime memory is not automatically authoritative.

## What did not change

- Documentation and code should evolve together.
- Product intent must survive agent and session boundaries.
- Later stages must preserve or explicitly revise earlier reasoning.
- Work must be bounded and verifiable.
- Evidence and operational learning must improve future decisions.
- The product repository owns its durable knowledge.

V2 changes the amount and timing of structure, not the lifecycle's purpose.

## Tradeoffs

The reset intentionally removes mature-looking surfaces such as the cockpit, proof packs, broad graph reports, compatibility documents, and exhaustive lifecycle templates. V2 initially provides fewer visible features, but each retained capability participates in one coherent end-to-end flow.

The previous implementation remains available through Git history and in the local ignored `v1/` snapshot used during the reset. New capabilities should return only when real workflows demonstrate that the simpler model needs them.

## Product promise

Echel should answer four questions better over time:

1. What does this product currently mean?
2. What is the safest and most valuable next step?
3. What context does an agent need for that step?
4. What evidence and learning should change the project's memory afterward?

Every future feature should strengthen one of these answers without making users manage Echel for its own sake.
