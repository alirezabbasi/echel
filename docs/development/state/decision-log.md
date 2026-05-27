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
