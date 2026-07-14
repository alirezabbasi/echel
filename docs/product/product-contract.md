# Echel 2 product contract

## Control

- Contract version: 1
- Product version: Echel 2
- Status: proposed for maintainer approval
- Authority: Echel maintainers
- Last reviewed: 2026-07-14
- Supersedes: broad “AI-native software engineering OS” positioning from Echel v1

This contract defines what Echel 2 is expected to accomplish and where its authority ends. Architecture, roadmap, and implementation decisions must preserve it or revise it through explicit maintainer review.

## Product problem

AI agents can generate and modify software quickly, but they do not inherently preserve a product’s business intent, domain meaning, architectural rationale, execution history, or operational learning across models, tools, sessions, and contributors.

Teams commonly respond with either unstructured conversation history or exhaustive process documentation. The former loses durable context; the latter becomes expensive to maintain and can create the appearance of certainty before knowledge exists. Existing codebases add a second problem: important behavior and architecture are already encoded in code, tests, configuration, Git history, and operations, but new work often begins without reconstructing that reality.

## Vision

Any founder, domain expert, or software team can use AI agents to create and continuously evolve a software product through a structured, repeatable, evidence-aware engineering methodology—without surrendering ownership of product knowledge to a model, agent runtime, or hosted platform.

## Business opportunity

Echel serves teams adopting multiple AI models and coding agents that need continuity and governance above individual execution tools. Its opportunity is to become the repository-native methodology and project-intelligence layer connecting product intent to agent-ready work and verified outcomes.

The opportunity remains a product hypothesis until validated through the benchmark and pilot work planned for Echel 2. Market size, pricing, packaging, and enterprise demand are intentionally outside this contract.

## Product promise

For a product at any lifecycle stage, Echel will make it possible to determine:

1. What is known, assumed, decided, disputed, or stale.
2. Where that knowledge came from and who approved it.
3. What work should happen next and why.
4. What exact context, constraints, permissions, and acceptance conditions an AI agent needs.
5. What evidence demonstrates that implementation satisfies intent.
6. What execution or production taught that should revise product knowledge.

## Entry mode A — Greenfield product creation

Starting from a raw idea, Echel progressively guides the user through:

```text
idea → problem → vision and opportunity → strategy → requirements
→ domain → architecture → roadmap → phases → tasks → repository
→ implementation → validation → deployment → operations and evolution
```

The lifecycle is progressive rather than document-first. Echel asks only questions material to the current decision, records uncertainty explicitly, and does not create empty future-stage artifacts. A safe experiment may begin before the entire lifecycle is mature.

The greenfield outcome is an implementation-ready product plan and repository whose work can be executed by AI agents without losing its upstream rationale.

## Entry mode B — Existing product evolution

Starting from an existing repository, Echel:

1. Safely inventories code, tests, configuration, documentation, Git history, CI, deployment, and operational knowledge.
2. Separates evidence-backed observations from higher-level inferences.
3. Proposes an understandable baseline for domain, architecture, workflows, conventions, risks, and unknown regions.
4. Lets authorized maintainers correct and approve that baseline.
5. Evaluates new requirements against the approved product and code reality.
6. Produces impact-aware plans and implementation-ready agent tasks.
7. Captures verification and operational learning through the same lifecycle used by greenfield products.

The brownfield outcome is a trusted, progressively improving system model that guides change without pretending repository analysis is complete or infallible.

## Shared lifecycle

The entry modes converge once Echel has enough approved knowledge to plan work. Both use the same canonical entities, task specification, context compiler, execution boundary, verification evidence, findings, and learning process.

The lifecycle is bidirectional. Implementation, validation, deployment, and operations may invalidate earlier assumptions, requirements, domain rules, or architecture. Echel must expose that impact and require an explicit resolution; it must not silently rewrite upstream truth to match code.

## Audiences and jobs

| Audience | Job to be done | Required outcome |
| --- | --- | --- |
| Founder or domain expert | Turn an idea and expertise into a viable product direction | Guided decisions without needing to understand Echel’s internal schema |
| Product manager | Preserve and evolve intent, scope, priority, and success measures | Strategy, requirements, roadmap, and change impact remain connected |
| Architect or technical lead | Understand or design the simplest sufficient system | Decisions are justified by product and domain constraints |
| AI-native developer | Delegate implementation safely across models and tools | Every agent receives a bounded, implementation-ready task specification |
| Reviewer, QA, or security specialist | Decide whether a change is acceptable | Acceptance, risk, provenance, and reproducible evidence are visible |
| Operator or maintainer | Evolve a live system without losing history | Releases, incidents, feedback, and learning revise future work |
| Platform integrator | Connect Echel to agent and engineering ecosystems | Stable runtime, analyzer, policy, evidence, and integration contracts |

## Responsibility boundary

### Echel is authoritative for

- software engineering methodology and lifecycle maturity;
- project knowledge, provenance, decisions, relationships, and findings;
- product and technical documentation derived from that knowledge;
- requirements, domain, architecture, roadmap, phases, and work planning;
- complete implementation-ready task specifications;
- minimal authoritative context compilation and change-impact analysis;
- verification policy, evidence relationships, review, release knowledge, and approved learning.

### Hermes is authoritative for

- model and provider selection and invocation;
- agent sessions, tool execution, skills, and generic runtime memory;
- context-window management inside an execution session;
- subagent delegation and code-generation execution;
- normalized execution output returned through the Echel runtime protocol.

Hermes memory and agent output are not product truth. They may propose findings or knowledge changes, but Echel applies project policy and human authority before acceptance.

### External engineering systems are authoritative for

- Git history, branches, worktrees, commits, and merge decisions;
- CI results, build artifacts, and deployment execution;
- identity providers, secrets, production telemetry, and source-host collaboration.

Echel references and interprets this evidence without duplicating ownership.

## Echel 2 core scope

- Local-first repository ownership and operation.
- Greenfield and brownfield initialization.
- Progressive lifecycle guidance and risk-sensitive maturity.
- Typed canonical knowledge with provenance and explicit relationships.
- Safe repository analysis with observation/inference separation.
- Requirements, domain, architecture, roadmap, phase, work, and task compilation.
- Minimal, explainable, token-budgeted agent context.
- Runtime-neutral execution contracts and a complete Hermes adapter.
- Isolated, observable, resumable agent runs.
- Automated and imported verification evidence.
- Review, release, deployment knowledge, operations findings, and approved learning.
- Stable CLI and library contracts, with optional local service and community extensions.
- Public documentation, examples, migrations, security policy, and cross-platform packaging.

## Explicit non-goals for Echel 2

- Building or training foundation models.
- Replacing Hermes or other general-purpose coding-agent runtimes.
- Replacing Git, CI, issue trackers, artifact registries, deployment systems, or telemetry platforms.
- Simulating a complete company through fixed fictional agent roles.
- Requiring every project to produce exhaustive strategy, DDD, architecture, governance, or operations documents.
- Treating generated documents, graph views, indexes, dashboards, chat history, or runtime memory as canonical truth.
- Guaranteeing that repository analysis fully reconstructs undocumented intent.
- Autonomous acceptance of consequential product decisions, policy exceptions, releases, or durable knowledge by default.
- A hosted multi-tenant control plane, marketplace, enterprise SSO, or regulated compliance packs before validated demand.
- Supporting every language, framework, agent runtime, or engineering integration in the 2.0 release.
- Generating an entire production application directly from one raw prompt without progressive decisions and verification.

## Product principles

1. Start with the minimum structured information.
2. Add structure only when current knowledge or risk requires it.
3. Keep one canonical, repository-owned representation of product truth.
4. Preserve provenance and distinguish fact, observation, inference, assumption, hypothesis, decision, and constraint.
5. Prefer sparse justified relationships to mechanically complete graphs.
6. Make later evidence capable of revising earlier reasoning.
7. Apply rigor proportional to project and change risk.
8. Let agents propose; let policy and authorized humans accept.
9. Keep methodology and execution-runtime responsibilities separate.
10. Explain every gate, recommendation, impact, and context inclusion.
11. Remain useful without a hosted Echel service or a functioning agent runtime.
12. Measure success through real project outcomes, not artifact counts.

## Initial success criteria

Echel 2 is successful when evidence demonstrates all of the following:

- A greenfield pilot reaches a verified MVP through progressively matured knowledge and Echel task specifications.
- A brownfield pilot establishes an approved baseline and ships a verified requirement change.
- Both journeys use the same canonical model and execution contract.
- Teams can switch Hermes models/providers without losing task meaning or product history.
- Agent task acceptance, rework, review defects, context precision, and onboarding time improve against a documented baseline.
- Every released change can be traced to intent, decisions, execution, verification, and operational learning where applicable.
- Users can understand current state and next action without navigating Echel’s storage taxonomy.

Exact benchmark thresholds belong to `E2-007`; this contract defines what must be measured without inventing unvalidated numbers.

## Evidence and assumptions

### Available evidence

- Echel v1 demonstrated that lifecycle artifacts, agent work packets, traceability, evidence, readiness, and operational learning can be connected in one repository.
- The v1 repository also demonstrated the cost of pre-created document trees, duplicated truth, inferred dense graph relationships, and methodology/runtime coupling.
- The project owner has explicitly restated both greenfield and brownfield workflows and the Echel/Hermes separation as the intended product vision.

### Unvalidated assumptions

- Target teams experience enough cross-agent context and intent loss to adopt a separate methodology and memory layer.
- Repository-native records will be accepted alongside existing issue trackers and product tools.
- Hermes provides a sufficiently stable execution boundary for the first complete adapter.
- The progressive methodology improves implementation outcomes enough to justify its learning cost.
- Community users prefer local ownership over an initially hosted experience.

These assumptions must be evaluated by `E2-006`, `E2-007`, greenfield and brownfield pilots, and the 2.0 benchmark. They must not be presented as market facts.

## Approval decision

Approval means maintainers agree that this document is the governing product contract for Echel 2 and that downstream terminology, architecture, roadmap, tasks, and public positioning must conform to it.

| Role | Name | Decision | Date | Notes |
| --- | --- | --- | --- | --- |
| Product owner/maintainer | Pending | Pending | Pending | Required to complete E2-001 |
| Independent reviewer | Pending | Pending | Pending | Confirms both entry modes and responsibility boundaries are unambiguous |

Until the required maintainer decision is recorded, this contract is proposed and `E2-001` remains in review rather than done.
