# Decision Log

## DEC-0001

- Decision: Keep scaffold defaults domain-agnostic.
- Context: Scaffold is intended as reusable starting point across projects.
- Impact: Domain-specific content must be ingested later as raw sources.

## DEC-0002

- Decision: Adopt a multi-loop project intelligence compounding model (delivery, reliability, strategy) as a guiding operating framework.
- Context: Project needed an explicit method for turning accumulated knowledge into future direction guidance.
- Impact: Bug management, RCA, and synthesis cadence become mandatory intelligence inputs for roadmap and architecture decisions.

## DEC-0003

- Decision: Evolve Echel into a four-layer operating system with explicit Knowledge, Execution, Evidence, and Automation contracts.
- Context: Knowledge scaffolding alone is insufficient for full lifecycle delivery, verification, release readiness, and operations.
- Impact: Lifecycle states, typed execution graph, proof-pack evidence model, and deterministic gate orchestration become first-class project primitives.

## DEC-0004

- Decision: Generated projects are rooted at the target software repository, with Echel relocated to an internal `echel-core/` directory that is ignored by the target project's Git history.
- Context: Echel should initialize and drive development without becoming the primary artifact pushed to the target project's remote.
- Impact: Wizard outputs and usage guidance must treat the target project root as the implementation surface, while `echel-core` remains an internal orchestration layer.

## DEC-0005

- Decision: Simplify visible Echel folders around human-readable purposes: knowledge, decisions, work, reports, development state, and bugs.
- Context: The previous numbered development folders and fine-grained wiki taxonomy made the system feel more complex and repetitive than necessary.
- Impact: Tools, bootstrap paths, wiki links, and governance checks must use the simplified structure.

## DEC-0006

- Decision: Generated projects keep `wiki/` at the target project root while framework files live under `echel-core/`.
- Context: Product intelligence belongs to the product repository, while Echel methodology and automation belong to the framework.
- Impact: `project.echel` now includes `WIKI_ROOT`; generated `echel-core/project.echel` points it to `../wiki`.

## DEC-0007

- Decision: Adopt `docs/development/methodology.md` as the Echel vNext methodology contract.
- Context: The methodology needs to define Echel as an AI-native software engineering operating system, not only a documentation framework or product wiki scaffold.
- Impact: Future lifecycle schemas, commands, templates, graph nodes, stage gates, cockpit flows, and agent playbooks must align with the ordered lifecycle from Product Discovery Specification through operations and governance.

## DEC-0008

- Decision: Define product-level lifecycle stages in `schema/lifecycle-stage.schema.md`.
- Context: The vNext methodology contract needed a deterministic schema for stage IDs, required artifacts, gate conditions, transitions, and blocking rules before runtime stage evaluation can be built.
- Impact: Future readiness, graph, cockpit, and CLI work should use this schema as the product-stage contract while `schema/EXECUTION.md` remains focused on execution node behavior.

## DEC-0009

- Decision: Introduce `wiki/requirements/` as the vNext requirements model before requirements automation.
- Context: Echel needs a stable, human-readable bridge from discovery, canon, and strategy into domain, architecture, planning, implementation, QA, and release work.
- Impact: Requirements now use stable IDs, source links, priority, phase, dependencies, risks, acceptance criteria, and verification methods. TASK-0013 can build `echel requirements` on top of these structures, and TASK-0014 can add a readiness gate without inventing the model during implementation.

## DEC-0010

- Decision: Treat canon as the immediate source for strategy generation and reject template-only content as lifecycle progress.
- Context: Review of TASK-0003 through TASK-0011 found that strategy generation read directly from discovery, canon drift was only memory-backed, discovery gate coverage was narrower than intended, and generated canon/strategy files could contain `TBD` boilerplate presented as real content.
- Impact: Discovery gates now check operator, business value, and non-template research content; canon generation only promotes meaningful source sections; canon drift writes `wiki/canon/canon-drift.md` and stale markers; strategy templates and generation reference canon as their immediate upstream source while keeping discovery traceability.

## DEC-0011

- Decision: Generate requirements into explicit generated sections and graph manual nodes instead of overwriting hand-authored requirement model context.
- Context: TASK-0012 established human-readable requirement model documents, while TASK-0013 needed automation that derives requirements from canon and strategy.
- Impact: `echel requirements` preserves authored requirement guidance, writes generated requirement/NFR/MVP/OOS/acceptance sections, rejects vague source language, marks phases, and adds requirement nodes plus source edges to `wiki/graph.manual.json` before regenerating `wiki/graph.json`.
