---
type: analysis
status: active
---
# Echel V2 Product Direction Review

## Review Scope

Reviewed repository structure, initialization flow, wiki model, development methodology, schemas, prompts, CLI tools, platform runtime, governance docs, current memory state, and task/ADR model against the goal of making Echel a platform people naturally use to create and evolve software products through AI-native workflows.

## Strategic Assessment

Echel has a strong conceptual core: persistent project intelligence that lets domain experts guide software creation while AI agents handle structured execution. The recent split between product-owned `wiki/` and framework-owned `echel-core/` is the right architectural direction.

The main gap is productization. Today Echel still feels like a framework scaffold and agent operating contract. V2 should become a guided product-creation platform where users express intent in natural product terms and Echel turns that intent into a living roadmap, architecture, tasks, evidence, and implementation loops.

## Current Strengths

- Clear thesis: AI context limits require durable project memory.
- Good separation emerging between product memory (`wiki/`) and framework method (`docs/development/`).
- Useful primitives exist: task artifacts, ADRs, health checks, evidence registry, memory records, conformance checks, provider-backed platform runtime.
- The four-layer model is directionally correct: Knowledge, Execution, Evidence, Automation.
- Initialization now supports a cleaner generated project topology.

## Current Weaknesses

- The primary user journey is not yet modeled as a product flow.
- The CLI exposes internal maintenance commands more strongly than domain-expert workflows.
- The wiki taxonomy is cleaner, but generated product memory still starts with framework concepts rather than the user's product problem, users, solution, scope, roadmap, and design direction.
- `docs/development` and schema rules describe process, but Echel does not yet actively guide the user through clarification, product shaping, prioritization, or acceptance definition.
- The web platform is currently chat plus command bridge; it is not yet a product cockpit.
- Evidence and gates exist, but they are not yet tied to user-facing milestones such as "MVP ready", "feature ready", or "release ready".
- Prompts are duplicated across agent tools and remain generic.
- The memory kernel is append/query oriented, but not yet an intelligence graph with first-class product concepts, relationships, contradictions, and roadmap synthesis.

## V2 North Star

Echel V2 should be:

> A product-creation operating system where a domain expert defines a problem and desired direction, and Echel continuously turns that intent into clarified requirements, product architecture, executable work, verified software, and compounding project intelligence.

The user should not feel they are managing markdown. They should feel they are steering a product.

## Recommended V2 Shape

### 1) Product-First Initialization

Replace scaffold-style initialization with a guided product definition flow:

- problem statement
- target users
- intended solution
- business or domain constraints
- MVP definition
- success criteria
- known risks
- preferred stack or existing codebase context
- decision style and quality threshold

Output should be a root-level product wiki initialized with product-owned pages:

- `project.md`
- `users.md`
- `problem.md`
- `solution.md`
- `scope.md`
- `roadmap.md`
- `architecture.md`
- `decisions/`
- `work/`
- `reports/`

Framework concepts should stay in `echel-core`, not dominate the product wiki.

### 2) A User-Facing Command Language

V2 should add commands that match how a product owner thinks:

- `echel define`: create or refine the product brief.
- `echel clarify`: ask targeted questions that reduce ambiguity.
- `echel plan`: generate roadmap, milestones, and executable work.
- `echel next`: choose the best next task based on priority, dependencies, and risk.
- `echel build`: prepare an agent-ready implementation packet.
- `echel review`: verify outcomes against acceptance criteria.
- `echel steer`: update product direction and propagate implications.
- `echel status`: show plain-language project state.

Internal commands like `doctor`, `wiki-health`, `conformance`, and `sync-memory` should remain available but become infrastructure beneath the product flow.

### 3) Product Intelligence Graph

The wiki should evolve from linked markdown into a typed product intelligence graph.

First-class nodes should include:

- problem
- user/persona
- use case
- requirement
- feature
- workflow
- component
- decision
- risk
- task
- evidence
- release

Relationships should be explicit:

- requirement implements solution goal
- feature serves user/persona
- task delivers feature
- decision constrains component
- evidence verifies task
- risk threatens release

This graph is what lets Echel reason across sessions instead of only storing notes.

### 4) Product Cockpit

The web platform should become the default user experience for non-technical users.

Recommended views:

- Product brief and current direction
- Clarification queue
- Roadmap and milestones
- Current sprint/work queue
- Architecture map
- Decisions and tradeoffs
- Risks and contradictions
- Agent activity and handoffs
- Evidence/readiness dashboard

The chat interface should be one interaction mode, not the whole product.

### 5) Agent Work Packets

Before implementation, Echel should generate structured packets for AI coding agents:

- task objective
- product context
- relevant architecture
- constraints
- acceptance criteria
- verification commands
- files likely involved
- required wiki updates
- evidence obligations

This is the bridge between domain-expert steering and reliable AI implementation.

### 6) Milestone and Release Readiness

Gates should be reframed around product milestones:

- idea clarified
- MVP scoped
- feature ready to build
- feature verified
- release candidate ready
- production ready

Each readiness state should include missing requirements, missing evidence, open risks, and recommended next actions.

### 7) Simpler Framework Core

`echel-core` should feel like runtime infrastructure:

- `bin/` or `tools/`: executable commands
- `method/`: Echel's operating method
- `schema/`: contracts
- `prompts/`: agent playbooks
- `runtime/`: platform state and adapters

The product root should remain minimal:

- source code
- `wiki/`
- product README
- product config if needed

### 8) Prompt Packs as Templates, Not Duplicates

The repeated prompt folders should become generated templates from one canonical playbook model. V2 should have lifecycle playbooks:

- define
- discover
- design
- build
- verify
- release
- operate
- steer

Tool-specific prompts can be rendered from those canonical playbooks.

## Recommended V2 Roadmap

### Phase 1: Product Creation Flow

- Add product-first initialization.
- Create product wiki templates.
- Add `define`, `clarify`, `plan`, `status`, and `next` commands.
- Keep current health/gate tooling beneath these workflows.

### Phase 2: Intelligence Graph

- Add typed product nodes and relationship metadata.
- Add graph validation and contradiction tracking.
- Generate roadmap and task suggestions from graph state.

### Phase 3: Agent Work Packets

- Add work-packet generation for coding agents.
- Add implementation handoff and review artifacts.
- Connect evidence obligations to each packet.

### Phase 4: Product Cockpit

- Replace the current chat-first UI with a cockpit organized around product direction, work, decisions, risks, and readiness.
- Keep chat as a steering interface.

### Phase 5: Release Readiness

- Add milestone/release readiness gates.
- Add proof packs and release summaries.
- Add user-facing explanations of what blocks progress.

## Design Principles for V2

- Product owners steer; Echel structures.
- The wiki is product memory, not framework documentation.
- Framework details live under `echel-core`.
- Every command should answer a product question.
- Agents should receive structured work packets, not vague chats.
- Gates should explain readiness in user language.
- Memory should become a graph of product reality, not only a folder of markdown.

## Key Recommendation

Do not make V2 primarily a better scaffold. Make it a guided product-creation platform.

The scaffold, docs, wiki, gates, prompts, and CLI are necessary infrastructure. The V2 product should be the experience that turns a domain expert's intent into an evolving software product with continuity, verification, and compounding intelligence.
