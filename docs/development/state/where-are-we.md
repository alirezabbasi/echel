# Where Are We

Last updated: 2026-07-14

## Completed

- Established Echel as a general-purpose LLM engineering scaffold.
- Added governance, execution, and memory control documents.
- Added the project intelligence compounding model as a canonical system artifact.
- Defined the four-layer OS model with v1 architecture/contracts for Execution, Evidence, and Automation layers.

## Recent

- Expanded the development loop to include bug management and RCA.
- Added an operational methodology doc for disciplined loop execution.
- Added Claude Code and Cursor prompt packs alongside Codex prompts.
- Added deterministic gate runner contract and evidence/proof-pack specifications.
- Clarified Echel as a domain-expert-guided AI-native development platform and documented the wiki/development-doc ownership boundary.
- Simplified the visible folder structure around human-readable purposes.
- Updated generated project topology so `wiki/` belongs to the product root and `docs/development/` stays inside `echel-core/`.

## Current

- Running v2 MVP foundation commands with declarative project contract loading.
- Enforcing integrity through `echel doctor` drift and evidence/gate reporting.
- Using `wiki/knowledge`, `wiki/decisions`, `wiki/work`, and `wiki/reports` as the project memory model.
- Using `WIKI_ROOT` so Echel can operate from `echel-core/` while maintaining root-level product memory.
- Completed Phase 1 deterministic product-owner workflows through `define`, `clarify`, `plan`, `status`, `next`, and `packet`.
- Completed Phase 2 product graph workflows through `graph`, `feature`, `risk`, and `link` commands.
- Completed Phase 3 graph-backed work packets and review reports through `build` and `review`.
- Completed Phase 4 product cockpit foundation over the wiki, graph, work, packets, reviews, risks, and decisions.
- Completed Phase 5 milestone readiness, proof packs, release summaries, and cockpit readiness.
- Completed V2 requirements hardening for initialization, commands, graph coverage, packets, cockpit, readiness, and framework-core boundaries.
- Added `docs/development/methodology.md` as the Echel vNext methodology contract for the full Product Discovery Specification to operations lifecycle.
- Added `schema/lifecycle-stage.schema.md` as the deterministic lifecycle stage contract for future stage gates and tooling.
- Added traceability, discovery, canon, strategy, and requirements model artifacts needed to preserve product intent from idea through execution planning.
- Re-approved TASK-0003 through TASK-0011 after tightening gates, canon drift handling, template promotion safeguards, and canon-driven strategy generation.
- Added the requirements command layer that turns canon and strategy into generated requirement rows and graph nodes without replacing hand-authored requirement context.
- Added the requirements readiness gate so `echel readiness --stage requirements` can block domain and architecture work until MVP requirements are testable, accepted, risk-aware, dependency-aware, scoped, and covered by NFRs.
- Added first-class domain model templates under `wiki/domain/`, including a complete current requirement-to-domain coverage map and technology-neutral domain guardrails.
- Added the domain command layer that turns requirement rows into generated domain concepts, contexts, aggregates, events, workflows, rules, and graph nodes without replacing authored domain guidance.
- Added the domain consistency gate so `echel readiness --stage domain` can block architecture until requirement coverage, domain ID integrity, graph coverage, duplicate-meaning checks, and technology-neutral language pass.
- Added the expanded architecture artifact model under `wiki/architecture/` so architecture can preserve domain boundaries, carry rationale, and prepare for generation and readiness gates.
- Added the architecture command layer that turns gated domain coverage into generated architecture rows and graph nodes without replacing authored architecture guidance.
- Added the architecture readiness gate so `echel readiness --stage architecture` can block roadmap work until deployment posture, data/security/observability models, ADR coverage, requirement/domain mappings, graph coverage, and complexity risk pass.
- Added the roadmap artifact expansion so `wiki/roadmap/` now contains master, MVP, architecture, engineering, and release roadmaps with phase objectives, scope, dependencies, demos, risks, and exit gates.
- Added execution phase artifacts under `wiki/execution/` so foundation, MVP, hardening, production, and evolution phases have task lists, dependencies, DoD, validation methods, documentation obligations, and expected repo changes.
- Added the execution task generator so `python3 tools/echel.py execution-tasks` creates 20 agent-executable `wiki/work/TASK-1xxx-*.md` records and `wiki/work/TASK_INDEX.md` from the phase artifacts.
- Added the repository factory generator so `python3 tools/echel.py repository-factory` creates `generated/product-repository/` with app/config/test/CI/env/local-doc baseline and a repository factory report.
- Added `wiki/engineering/` as the product-owned engineering contract and made generated setup, start, syntax-lint, test, CI, and verification commands exact and reproducible.
- Added the vNext AI-agent role model in `wiki/agents/role-model.md` and `docs/development/methodology.md`: all 13 roles (Founder Interviewer through Governance Auditor) now define responsibilities, inputs, outputs, and forbidden actions, with a lifecycle-stage mapping and a shared binding to `wiki/engineering/development-workflow.md`.
- Added canonical lifecycle playbooks under `prompts/playbooks/` and tool render maps for Codex, Claude Code, and Cursor so tool-specific prompts derive from one guarded lifecycle prompt source.
- Added `wiki/agents/handoff-protocol.md` so lifecycle stage outputs preserve assumptions, risks, unresolved questions, evidence, stale artifacts, and next-stage instructions in a required Handoff Summary.
- Expanded graph lifecycle coverage so `wiki/graph.json` now includes first-class nodes for discovery items, assumptions, hypotheses, buyers, stakeholders, strategy, requirements, domain concepts, bounded contexts, business rules, architecture components, tests, deployment artifacts, operation artifacts, contradictions, and learnings.
- Added graph metadata enrichment so graph nodes carry statement type, confidence, source stage, and verification status, with unresolved low-confidence assumptions treated as critical graph validation issues.
- Added the traceability matrix command and report so lifecycle coverage is visible from discovery through evidence, with canon and evidence gaps reported as broken chains.
- Added the validation artifact surface under `wiki/validation/` so requirements, tasks, domain concepts, and acceptance criteria can be mapped before validation execution is automated.
- Added the validation command so mapped validation artifacts are summarized into reports and graph test/evidence target nodes.
- Added the evidence registration command so agents can create checksum-backed evidence records and graph evidence nodes without hand-editing JSON.
- Added the deployment artifact surface under `wiki/deployment/` so release gates can evaluate deployment path, environments, rollback, secrets, and production checklist state.
- Added the release readiness gate so `python3 tools/echel.py readiness --stage release` blocks unresolved validation blockers, deployment gaps, rollback gaps, checklist gaps, missing evidence, and unmitigated risks.
- Added the operations artifact surface under `wiki/operations/` so support handoff, observability, incident severity/escalation, backup/recovery, SLA/SLO, change control, and evolution backlog governance have durable memory.
- Updated graph generation so operations documents appear as operations-stage `operation-artifact` nodes.
- Added the learning loop command and artifact structure so post-release signals can create task, ADR, risk, assumption, or strategy-change follow-ups.
- Redesigned the cockpit as a lifecycle steering surface. Discovery through Governance are now the primary navigation model, and every stage exposes blockers, next action, responsible AI role, artifacts, and safe action metadata.
- Added guided cockpit actions for native stage workflows, including discovery field updates, lifecycle artifact generation, readiness checks, work packets, validation summaries, evidence registration, proof/release summaries, operation learning capture, graph reports, and traceability.
- Added the governance artifact surface under `wiki/governance/`, including documentation governance, architecture governance, ADR process, traceability model, quality gates, and repository integrity audit baseline.
- Added the repository integrity audit command so `python3 tools/echel.py integrity audit` reports missing docs, stale docs, broken traceability, missing ADRs, missing tests, missing evidence, and methodology violations.
- Added the contradiction register command so `python3 tools/echel.py contradictions sync` turns local contradiction records into `wiki/governance/contradictions.md`, graph contradiction nodes, and explicit resolution tasks.
- Added the migration compatibility command so `python3 tools/echel.py migration compatibility` preserves root wiki pages, maps them to lifecycle artifacts, and keeps old links valid while vNext folders become canonical.
- Updated initialization so new projects start with the methodology-complete root `wiki/` lifecycle surface while the Echel framework remains isolated under `echel-core/`.
- Added generated-project vNext verification through `make verify-vnext-generated`, proving lifecycle structure, core command execution from `echel-core/`, and product-wiki separation.
- Rewrote the README to present Echel as a complete AI-native Product-to-Repository Factory and to distinguish methodology, product memory, graph, cockpit, agents, evidence, and readiness.
- Added the vNext technical quick start command sequence so the docs now show the full lifecycle order from `discover` through `operate`, including current Echel command equivalents for roadmap, planning, build, release, and operations handoff.
- Added the vNext proof pack so `python3 tools/echel.py proof-pack --target vnext` writes methodology coverage, command coverage, graph coverage, cockpit coverage, and remaining risks into one certification artifact.
- Added the final vNext readiness gate so `python3 tools/echel.py vnext-final` writes the final certification report and vNext release summary.

## Next

1. Resolve final vNext gate blockers around historical evidence references and open review checks.
2. Expand release readiness into production operation checks once operations gates are implemented.
3. Continue hardening graph-backed traceability around canon statements and evidence coverage.

## Risks/Blocks

- Contract drift across docs/schema/tools could weaken deterministic validation if not gated.
- Adding new folders without a unique purpose could reintroduce navigation complexity.
- Template-derived content must not be promoted into canon or strategy as product truth.
- Traceability reporting still shows canon statement gaps until canon nodes are generated; release readiness, learning capture, and cockpit lifecycle steering/actions are executable, while operations readiness still needs a dedicated gate.
