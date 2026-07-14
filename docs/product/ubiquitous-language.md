# Echel 2 ubiquitous language

## Control

- Contract version: 1
- Product version: Echel 2
- Status: accepted
- Authority: Echel maintainers
- Last reviewed: 2026-07-14
- Depends on: [Echel 2 product contract](product-contract.md)

This glossary is the naming contract for public documentation, schemas, commands, APIs, task specifications, and architectural decisions. A public term has exactly one meaning. When a more precise everyday phrase is clearer in user-facing text, it may be used only if it does not introduce a second domain concept.

## Core product boundary

| Term | Definition |
| --- | --- |
| **Echel** | The repository-native methodology and project-intelligence platform that preserves product knowledge, guides lifecycle decisions, plans work, compiles task context, and relates outcomes back to intent. Echel does not execute model or tool loops. |
| **Hermes** | The first supported agent runtime: it selects and invokes models, runs tools and skills, manages sessions and bounded delegation, and returns execution results through the runtime protocol. Hermes does not own product truth. |
| **runtime** | An external execution system that accepts an Echel task specification and context bundle and returns normalized events and results. Hermes is a runtime, not a synonym for runtime. |
| **runtime adapter** | An integration that translates the versioned Echel runtime protocol to one runtime without moving runtime-specific behavior into Echel's domain. |
| **external engineering system** | A system authoritative for an engineering concern outside Echel, such as Git for revision history, CI for build execution, or a deployment platform for deployment execution. |
| **project** | The software product and its evolving business and technical knowledge. It is not merely a repository checkout. |
| **repository** | The Git-controlled workspace containing source code and repository-owned Echel records. Git remains authoritative for revision history. |

## Knowledge and authority

| Term | Definition |
| --- | --- |
| **product knowledge** | Durable, repository-owned information about the product's intent, reality, decisions, work, and outcomes. Only canonical records constitute product knowledge. |
| **canonical record** | The single authoritative, versioned representation of one product-knowledge item. Rendered documents, indexes, runtime memory, and external tracker copies are not canonical records. |
| **provenance** | The source, author or actor, time, and revision information needed to explain how a knowledge item arose. |
| **evidence** | A reference to an observable source or result that supports or challenges a knowledge item or acceptance condition. Evidence is not automatically proof or approval. |
| **fact** | A proposition accepted as true under project authority and supported by identified evidence. New evidence may challenge it. |
| **observation** | A directly detected or reported condition, recorded without claiming its broader meaning. Repository analysis produces observations first. |
| **inference** | An interpretation derived from observations or other knowledge; it must identify its basis and remain distinguishable from fact. |
| **assumption** | A proposition temporarily used for planning despite insufficient validation. |
| **hypothesis** | A testable proposition with a stated validation approach. |
| **constraint** | An accepted limit that narrows valid product or implementation choices. |
| **decision** | An explicitly approved choice with rationale, authority, and consequences. |
| **finding** | A newly discovered issue, contradiction, risk, or learning that requires evaluation before it changes accepted knowledge. |
| **proposal** | A candidate mutation to canonical product knowledge awaiting an authorized decision. Agent output enters Echel as a proposal or finding, never as accepted truth. |
| **relationship** | An explicit, typed, justified connection between canonical records. Absence of a relationship means unknown, not unrelated. |
| **projection** | A deterministic, disposable human- or machine-readable view derived from canonical records. Documentation pages and reports may be projections. |
| **index** | A disposable structure optimized for search or traversal and rebuildable from canonical records. |
| **runtime memory** | Session or execution memory owned by a runtime. It may inform proposals but is never product knowledge by itself. |

## Lifecycle and planning

| Term | Definition |
| --- | --- |
| **entry mode** | The way a project begins using Echel: **greenfield** from an idea or **brownfield** from an existing repository. Entry modes converge on the same lifecycle and canonical model. |
| **greenfield** | The entry mode that progressively develops an initial idea into enough accepted product knowledge to plan and implement it. |
| **brownfield** | The entry mode that analyzes an existing repository, separates observations from inferences, and establishes an approved baseline before managing change. |
| **baseline** | The reviewed set of current brownfield observations, inferences, and accepted knowledge used to reason about future changes. It is explicitly incomplete and revisable. |
| **lifecycle stage** | A named area of product maturity—such as problem, strategy, domain, architecture, or operations—not a required folder or linear approval gate. |
| **maturity** | The evidence-backed readiness of current knowledge for a particular next decision. Maturity is risk-sensitive and may move backward when evidence invalidates earlier knowledge. |
| **methodology skill** | A bounded, repeatable Echel procedure that helps create or evaluate product knowledge. It defines engineering reasoning, not model invocation. |
| **roadmap** | An ordered set of desired product outcomes and dependencies. It is not a list of implementation tasks. |
| **phase** | A coherent increment of roadmap outcomes that can be planned and evaluated together. |
| **work item** | A mutable planning record describing a desired engineering outcome, priority, dependencies, and current state. |
| **task specification** | An immutable, implementation-ready execution contract compiled from one work item at a known revision. It includes objective, scope, constraints, acceptance conditions, permissions, and verification. |
| **context bundle** | The minimal, explainable, revision-bound selection of authoritative knowledge and supporting material supplied with a task specification. |
| **context compiler** | The deterministic Echel component that selects, ranks, budgets, and explains a context bundle. It does not summarize away authoritative constraints. |
| **run** | One runtime execution attempt against an immutable task specification. A run can produce code, events, evidence, findings, and proposals, but cannot approve its own durable knowledge changes. |
| **acceptance condition** | A testable statement that must be supported by evidence before work is accepted. |
| **verification** | The reproducible process of collecting and evaluating evidence against acceptance conditions and policy. |
| **release** | An approved grouping of verified changes and their evidence, referenced by Echel but versioned and distributed through external engineering systems. |
| **operational learning** | Evidence or findings from deployment and operation that may propose revisions to earlier product knowledge. |

## Naming rules

1. Use the canonical singular term for a domain concept in schemas, APIs, commands, and task packets.
2. Do not use `memory` alone. Say **product knowledge**, **canonical record**, **context bundle**, or **runtime memory** according to ownership and purpose.
3. Do not use `agent` to mean Echel. An **agent** is an execution participant owned by a runtime; a **methodology skill** is Echel guidance.
4. Do not call repository analysis a fact-extraction process. It records observations and separately proposes inferences.
5. Use **accepted** only for a decision made under Echel authority. Use **generated**, **detected**, **proposed**, or **verified** for their distinct states.
6. A document is a canonical record only if its contract explicitly declares it so. Otherwise it is a projection or supporting material.
7. Prefer **relationship** over `graph edge`; a graph is only one possible projection or index.
8. New public abbreviations require a glossary entry. Identifiers may use stable prefixes, but prefixes do not create new concepts.

## Echel v1 terminology migration

These mappings govern new work. Migration tooling may continue to recognize a v1 term as input, but public v2 output must use the v2 term and explain any lossy mapping.

| Echel v1 term | Echel 2 treatment | Reason |
| --- | --- | --- |
| `wiki` | Retire; use **product knowledge** for authority or **projection** for rendered pages | A wiki mixed storage, navigation, and truth. |
| `product graph` / `knowledge graph` | Retire as a canonical concept; use **canonical records and explicit relationships**, with an **index** or **projection** for graph traversal | The graph duplicated authority and encouraged unjustified dense links. |
| `memory kernel` | Split into **canonical record store**, **context compiler**, and **runtime memory** | The term crossed Echel/Hermes ownership boundaries. |
| `canon` | Use **accepted product knowledge** or name the governing **contract** | “Canon” hid record state and authority. |
| `work packet` | Use **task specification** | The v2 term emphasizes an immutable execution contract. |
| `proof pack` | Use **verification evidence** or **release evidence projection** | Evidence supports a decision; it is not universal proof. |
| `evidence registry` | Use **evidence records** and an optional **evidence index** | A registry must not become a second source of truth. |
| `readiness report` | Use **maturity assessment** or **policy assessment** | Readiness depends on the decision and risk, not one universal score. |
| `stage gate` | Use **maturity decision** or **policy check** | Lifecycle stages are not mandatory linear gates. |
| `cockpit` | Retire; name the concrete **status view**, **next-action view**, CLI, TUI, or future UI | A metaphor does not define behavior. |
| `virtual delivery team` / fixed agent roles | Use runtime-owned **agents** with bounded capabilities; use Echel **methodology skills** for engineering procedures | Fictional roles coupled methodology to execution. |
| `Echel Core` | Use the concrete component name, such as **canonical record store** or **context compiler** | A catch-all core obscured responsibility. |
| `AI-native software engineering OS` | Use **repository-native methodology and project-intelligence platform** | Echel coordinates knowledge and methodology; it does not own every engineering system. |

## Governance

- A new public concept requires a definition, an owner, examples or affected interfaces, and review for overlap with this glossary.
- A changed meaning requires a new contract revision and a migration note; silently redefining an existing term is prohibited.
- An implementation-local name does not need a glossary entry unless it crosses a public contract or creates domain meaning.
- When two terms appear interchangeable, maintainers must select one canonical term or document a meaningful distinction before either enters a public interface.
- Code and documentation that conflict with this glossary create a finding. They do not implicitly revise the glossary.

## Reference-journey check

In greenfield work, an assumption about a raw idea can mature into an accepted fact or decision only through evidence and authority; it then informs a work item, task specification, and context bundle. In brownfield work, repository analysis first creates observations, then proposes inferences for the baseline. Both journeys produce the same task specification and use the same runtime boundary. Results from Hermes return as run evidence, findings, or proposals and require Echel policy and authorized review before changing product knowledge.
