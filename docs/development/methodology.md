---
type: methodology
status: active
---
# Echel vNext Methodology Contract

## Purpose

Echel is an AI-native software engineering operating system. Its job is to turn a raw product idea into a production-ready software repository through a controlled lifecycle of discovery, canon, strategy, requirements, domain modeling, architecture, execution, validation, release, operations, and continuous evolution.

Echel is not only a documentation framework. Documentation is one interface to the operating system, but the operating system must also preserve project memory, enforce traceability, generate agent-ready work, verify evidence, detect drift, and prevent AI agents from building from vague intent.

## Core Principle

Do not let an AI agent write product code directly from an idea.

Every implementation must be downstream of:

```text
Product Discovery Specification
-> Product Canon
-> Product Strategy
-> Requirements
-> Domain Model
-> Architecture
-> Roadmap
-> Execution Plan
-> Agent Task
-> Verification
-> Updated Memory
```

If any required upstream stage is missing, incomplete, stale, or contradicted, Echel must block or clearly warn before later-stage work proceeds.

## Operating Boundary

Echel uses two complementary memory surfaces:

- `wiki/`: product-owned durable memory, including discovery, canon, strategy, requirements, domain knowledge, architecture, work, decisions, reports, release state, and operations knowledge.
- `docs/development/`: Echel Core operating method, lifecycle rules, execution controls, evidence contracts, automation contracts, and active framework state.

Generated target projects keep `wiki/` at the product repository root. Echel Core lives under `echel-core/` and resolves product memory through `WIKI_ROOT`.

## Source-of-Truth Hierarchy

When artifacts disagree, resolve conflicts using this hierarchy:

1. Accepted decisions and explicit owner updates.
2. Product Discovery Specification facts and constraints.
3. Product Canon.
4. Product Strategy.
5. Requirements and acceptance criteria.
6. Domain model.
7. Architecture and ADRs.
8. Roadmap and execution plan.
9. Agent tasks and work packets.
10. Code, tests, verification evidence, release, and operations records.

Lower-level artifacts must reference and refine higher-level artifacts rather than reinterpret them silently. If a lower-level artifact reveals that an upstream artifact is wrong, create a contradiction or decision artifact and propagate the change through dependent stages.

## Statement Discipline

Important product statements must identify their type and confidence.

Statement types:

- `fact`: verified information.
- `observation`: directly observed information.
- `assumption`: believed but unverified.
- `hypothesis`: claim that must be tested.
- `decision`: explicit choice.
- `constraint`: limitation that cannot be violated.
- `risk`: possible negative outcome.
- `question`: unresolved item.

Confidence levels:

- `high`: strong evidence or owner certainty.
- `medium`: plausible but still needs validation.
- `low`: weakly supported or exploratory.

AI agents must not treat assumptions or hypotheses as facts. Low-confidence assumptions that materially affect scope, architecture, or release readiness must remain visible until resolved or accepted.

## Traceability Contract

Every important item should receive a stable methodology ID.

Recommended ID families:

- `P-###`: problem or pain.
- `U-###`: user.
- `B-###`: buyer or business stakeholder.
- `A-###`: assumption.
- `H-###`: hypothesis.
- `R-###`: risk.
- `S-###`: success criterion.
- `BR-###`: business rule.
- `Q-###`: question.
- `REQ-###`: requirement.
- `DM-###`: domain concept.
- `BC-###`: bounded context.
- `AGG-###`: domain aggregate.
- `DE-###`: domain event.
- `ADR-####`: architectural decision.
- `TASK-####`: execution task.
- `TEST-###`: test or validation case.
- `EVID-###`: evidence artifact.

Downstream artifacts must preserve links to upstream IDs. A complete chain should be able to show:

```text
discovery item -> canon statement -> strategy choice -> requirement -> domain concept -> architecture decision -> task -> test -> evidence -> release or operations record
```

The product graph must preserve this lifecycle shape. First-class graph node types now cover discovery items, assumptions, hypotheses, buyers, stakeholders, strategies, requirements, domain concepts, bounded contexts, business rules, architecture components, tests, deployment artifacts, operation artifacts, governance artifacts, contradictions, and learnings. Graph nodes also carry statement type, confidence, source stage, verification status, and trace ID metadata where available so agents can distinguish facts, assumptions, hypotheses, decisions, constraints, and evidence.

## Lifecycle Stages

### Stage 0: Repository Initialization

Objective: create the empty execution container and product memory boundary.

Inputs:

- Product name.
- Short raw idea.
- Existing repository path, when onboarding brownfield work.

Outputs:

- Product repository root.
- Product-owned `wiki/`.
- Internal `echel-core/`.
- Initial configuration and operating docs.

Required artifacts:

- Product README.
- `wiki/project.md`.
- `wiki/log.md`.
- `echel-core/project.echel`.

Decisions:

- Scratch or existing project mode.
- Repository ownership boundary.
- Initial product memory location.

Acceptance criteria:

- Repository structure is clear.
- Product memory is committed with the product.
- Echel Core is isolated as framework machinery.
- No product implementation starts yet.

Prepares next stage by giving discovery a durable place to capture founder intent.

### Stage 1: Product Discovery

Objective: convert the raw idea into a Product Discovery Specification that prevents AI guessing.

Inputs:

- Founder/domain-expert intent.
- Raw notes, references, sketches, links, and constraints.

Outputs:

- Product Discovery Specification.
- Research plan.
- Initial assumptions, risks, questions, and success criteria.

Required artifacts:

- `wiki/discovery/product-discovery-spec.md`.
- `wiki/discovery/research-plan.md`.
- `wiki/discovery/assumptions.md`.

Decisions:

- What problem hurts.
- Who experiences it.
- Who pays, approves, blocks, operates, and influences.
- What is in scope and out of scope.
- What must be researched before later stages.

Acceptance criteria:

- Problem is clearly defined.
- Buyer, user, and operator are separated.
- Current workflow is documented without the proposed product.
- Business value and success criteria are measurable.
- Non-goals, constraints, risks, assumptions, open questions, and research plan exist.
- Important statements include type, confidence, and traceability IDs.

Gate rule:

- Do not proceed to canon if discovery is incomplete.

Prepares next stage by creating the founder/platform contract.

### Stage 2: Product Canon

Objective: define the stable product truth that downstream stages must obey.

Inputs:

- Product Discovery Specification.
- Resolved discovery questions.

Outputs:

- Product identity.
- Product vision.
- Product principles.
- Non-negotiable constraints.

Required artifacts:

- `wiki/canon/product-canon.md`.
- `wiki/canon/vision.md`.
- `wiki/canon/product-principles.md`.
- `wiki/canon/non-negotiables.md`.

Decisions:

- What the product is.
- What the product is not.
- Why it exists.
- Who it serves.
- Why customers would pay.
- What must never be compromised.

Acceptance criteria:

- Canon references discovery IDs.
- Vision is specific and not buzzword-driven.
- Product identity is stable enough for strategy.
- Strategic and execution risks are visible.

Gate rule:

- Do not proceed to strategy if canon contradicts unresolved discovery items.

Prepares next stage by making strategy a refinement of product truth.

### Stage 3: Product Strategy

Objective: turn product truth into a market wedge and business plan.

Inputs:

- Product Canon.
- Discovery buyer/user/stakeholder model.
- Competitive alternatives and current workflows.

Outputs:

- ICP.
- Buyer/user model.
- Market wedge.
- Positioning.
- Pricing hypothesis.
- PMF evidence plan.

Required artifacts:

- `wiki/strategy/icp.md`.
- `wiki/strategy/buyer-user-model.md`.
- `wiki/strategy/market-wedge.md`.
- `wiki/strategy/competitive-analysis.md`.
- `wiki/strategy/positioning.md`.
- `wiki/strategy/pricing-and-packaging.md`.
- `wiki/strategy/pmf-evidence.md`.

Decisions:

- First customer segment.
- First painful use case.
- Initial pricing and packaging logic.
- Main adoption blockers.
- Evidence required to continue or stop.

Acceptance criteria:

- One clear initial market wedge exists.
- Buyer is not confused with user.
- MVP can plausibly be sold or validated.
- PMF evidence is measurable.
- Pricing remains marked as hypothesis unless validated.

Gate rule:

- Do not proceed to requirements if target customer, buyer, wedge, or PMF evidence is vague.

Prepares next stage by defining buildable business scope.

### Stage 4: Requirements

Objective: convert strategy into testable build scope.

Inputs:

- Product Strategy.
- Product Canon.
- Discovery constraints and business rules.

Outputs:

- Product requirements.
- Functional requirements.
- Non-functional requirements.
- MVP scope.
- Out-of-scope list.
- Acceptance criteria.

Required artifacts:

- `wiki/requirements/product-requirements.md`.
- `wiki/requirements/functional-requirements.md`.
- `wiki/requirements/non-functional-requirements.md`.
- `wiki/requirements/mvp-scope.md`.
- `wiki/requirements/out-of-scope.md`.
- `wiki/requirements/acceptance-criteria.md`.

Decisions:

- MVP versus later scope.
- Must-have versus optional behavior.
- Performance, security, compliance, reliability, and usability expectations.
- Explicit exclusions.

Acceptance criteria:

- Every requirement has an ID.
- Every requirement links to upstream source IDs.
- Every requirement is testable.
- MVP is small enough to build and validate.
- Dependencies and risks are visible.

Gate rule:

- Do not proceed to domain modeling if MVP requirements are vague or untestable.

Prepares next stage by defining what the domain must explain.

### Stage 5: Domain Model

Objective: define product language and business rules before technical architecture.

Inputs:

- Requirements.
- Discovery business rules.
- Current workflows and target workflows.

Outputs:

- Ubiquitous language.
- Bounded contexts.
- Entities and aggregates.
- Domain events.
- Workflows.
- Policies and rules.

Required artifacts:

- `wiki/domain/domain-overview.md`.
- `wiki/domain/ubiquitous-language.md`.
- `wiki/domain/bounded-contexts.md`.
- `wiki/domain/entities.md`.
- `wiki/domain/aggregates.md`.
- `wiki/domain/domain-events.md`.
- `wiki/domain/workflows.md`.
- `wiki/domain/policies-and-rules.md`.

Decisions:

- Core concepts and definitions.
- Ownership boundaries.
- Workflow lifecycle.
- Domain events and policies.
- Forbidden responsibilities for each bounded context.

Acceptance criteria:

- Every requirement maps to domain concepts.
- Every important term has one definition.
- Business rules are separate from database design.
- Technology choices are not introduced unless they are explicit constraints.

Gate rule:

- Do not proceed to architecture if domain terms, boundaries, or business rules are unstable.
- `GATE-DOMAIN` must pass before architecture work. It checks requirement coverage, domain ID reference integrity, duplicate meanings, undefined references, generated graph coverage, and concrete technology leakage.

Prepares next stage by giving architecture stable semantic boundaries.

### Stage 6: Architecture

Objective: decide how the system will be built while preserving domain boundaries.

Inputs:

- Domain Model.
- Requirements.
- Non-functional expectations.
- Constraints.

Outputs:

- Architecture overview.
- Context map.
- Component, data, API, event, workflow, security, and observability architecture.
- ADRs for major decisions.

Required artifacts:

- `wiki/architecture/overview.md`.
- `wiki/architecture/context-map.md`.
- `wiki/architecture/component-architecture.md`.
- `wiki/architecture/data-architecture.md`.
- `wiki/architecture/api-architecture.md`.
- `wiki/architecture/event-architecture.md`.
- `wiki/architecture/workflow-architecture.md`.
- `wiki/architecture/security-architecture.md`.
- `wiki/architecture/observability-architecture.md`.
- `wiki/decisions/ADR-*.md`.

Decisions:

- Monolith, modular monolith, services, or other system shape.
- Data strategy.
- API style.
- Eventing and workflow strategy.
- Authentication and authorization.
- Deployment and integration boundaries.

Acceptance criteria:

- Every major architectural choice has rationale.
- Alternatives and rollback strategies exist for major decisions.
- Complexity is justified.
- Architecture maps to requirements and domain contexts.

Gate rule:

- Do not proceed to roadmap if architecture lacks required decision coverage or violates domain boundaries.
- `echel architecture` generates architecture mappings only after `GATE-DOMAIN` passes unless explicitly forced. Generated mappings must preserve requirement IDs, domain IDs, rationale, and ADR suggestions.
- `GATE-ARCHITECTURE` must pass before roadmap work. It checks the expanded architecture artifact surface, deployment posture, data strategy, security model, observability model, ADR coverage for accepted major decisions, requirement/domain mappings, generated graph coverage, and unjustified overengineering risk.

Prepares next stage by defining build phases around real system structure.

### Stage 7: Roadmap

Objective: turn architecture into phased delivery that produces a usable product early.

Inputs:

- Architecture.
- Requirements.
- Strategy and MVP scope.
- Risks and constraints.

Outputs:

- Master roadmap.
- MVP roadmap.
- Architecture roadmap.
- Engineering roadmap.
- Release plan.

Required artifacts:

- `wiki/roadmap/master-roadmap.md`.
- `wiki/roadmap/mvp-roadmap.md`.
- `wiki/roadmap/architecture-roadmap.md`.
- `wiki/roadmap/engineering-roadmap.md`.
- `wiki/roadmap/release-plan.md`.

Decisions:

- Build sequence.
- Phase boundaries.
- Dependencies.
- Demo milestones.
- Release sequence.

Acceptance criteria:

- Roadmap is executable.
- MVP proves the product direction.
- No phase depends on undefined work.
- Every phase has outputs, risks, demo scenario, and exit gate.

Gate rule:

- Do not create agent tasks from roadmap items that lack acceptance criteria and dependencies.
- TASK-0021 provides the authored roadmap artifact model under `wiki/roadmap/`. TASK-0022 must consume these roadmap artifacts when creating execution phase documents.

Prepares next stage by defining execution slices.

### Stage 8: Execution Planning

Objective: create phases and tasks that AI agents can execute safely.

Inputs:

- Roadmap.
- Architecture.
- Requirements.
- Domain model.

Outputs:

- Execution phases.
- Detailed implementation tasks.
- Work packets.

Required artifacts:

- `wiki/execution/phase-0-foundation.md`.
- `wiki/execution/phase-1-mvp.md`.
- `wiki/execution/phase-2-hardening.md`.
- `wiki/execution/phase-3-production.md`.
- `wiki/execution/phase-4-evolution.md`.
- `wiki/work/TASK-*.md`.
- `wiki/reports/work-packets/*.md`.

Decisions:

- Task boundaries.
- Dependencies.
- Required files and verification commands.
- Definition of done.
- Rollback notes.

Acceptance criteria:

- Every task is small enough for one AI coding session.
- Every task has objective, business reason, technical scope, dependencies, acceptance criteria, tests, validation command, documentation updates, and out-of-scope.
- No task mixes unrelated concerns.

Gate rule:

- Do not let an implementation agent start without a task and work packet.
- TASK-0022 provides the authored execution phase artifacts under `wiki/execution/`.
- TASK-0023 adds `python3 tools/echel.py execution-tasks`, which reads each phase task row and generates detailed `wiki/work/TASK-1xxx-*.md` records plus `wiki/work/TASK_INDEX.md`.
- The command requires `GATE-ARCHITECTURE` to pass unless `--force` is used for draft task generation.

Prepares next stage by producing safe agent execution inputs.

### Stage 9: Repository Factory

Objective: create or update the production codebase skeleton from architecture and execution tasks.

Inputs:

- Architecture.
- Execution plan.
- Engineering constraints.

Outputs:

- Application folder structure.
- Configuration structure.
- Test structure.
- CI skeleton.
- Environment examples.
- Local development docs.
- Repository factory report.

Required artifacts:

- `generated/product-repository/README.md`.
- `generated/product-repository/app/`.
- `generated/product-repository/config/`.
- `generated/product-repository/tests/`.
- `generated/product-repository/.github/workflows/ci.yml`.
- `generated/product-repository/.env.example`.
- `wiki/reports/repository-factory/generated-repository.md`.
- `wiki/engineering/repository-structure.md`.
- `wiki/engineering/coding-standards.md`.
- `wiki/engineering/development-workflow.md`.
- `wiki/engineering/configuration-strategy.md`.
- `wiki/engineering/local-development.md`.

Decisions:

- Repository layout.
- Dependency and package strategy.
- Local boot command.
- Test and lint commands.
- Configuration and environment handling.

Acceptance criteria:

- Repository can install and boot locally.
- Health check or equivalent baseline exists.
- Tests and linting can run.
- README contains exact commands.

Gate rule:

- Do not start feature implementation before baseline verification exists.
- TASK-0024 provides the architecture- and task-derived baseline through `python3 tools/echel.py repository-factory`.
- TASK-0025 establishes `wiki/engineering/` as the product-owned engineering contract and synchronizes exact setup, start, syntax-lint, test, and verification commands across the generated README, CI, and verification script.

Prepares next stage by giving agents an executable baseline.

### Stage 10: Implementation

Objective: build one small verified task at a time.

Inputs:

- Work packet.
- Task artifact.
- Product Canon.
- Relevant requirements, domain model, architecture, and current state.

Outputs:

- Code changes.
- Tests.
- Updated docs and memory.
- Evidence.
- Review report.

Required artifacts:

- Modified source files.
- Tests.
- `wiki/reports/reviews/*.md`.
- Evidence registry entries.
- Updated task and product memory.

Decisions:

- Only local implementation choices inside task scope.
- New architecture decisions require ADRs.

Acceptance criteria:

- Task scope is satisfied.
- Tests and validation commands pass.
- Architecture compliance is checked.
- Evidence is registered.
- Product memory is updated.

Gate rule:

- A task is not done unless it produces modified files, runnable proof, tests, architecture compliance verification, and updated memory.

Prepares next stage by producing verifiable behavior.

### Stage 11: Validation

Objective: prove that the product works against requirements and acceptance criteria.

Inputs:

- Implemented behavior.
- Requirements.
- Domain model.
- Tasks.
- Evidence.

Outputs:

- Test strategy.
- Acceptance tests.
- Integration and end-to-end tests.
- Security and performance checks where relevant.
- Validation report.

Required artifacts:

- `wiki/validation/test-strategy.md`.
- `wiki/validation/acceptance-tests.md`.
- `wiki/validation/integration-tests.md`.
- `wiki/validation/e2e-tests.md`.
- `wiki/validation/security-tests.md`.
- `wiki/validation/performance-tests.md`.
- `wiki/validation/validation-report.md`.

Decisions:

- Which risks require explicit validation.
- Which failures block release.
- Which exceptions are accepted.

Acceptance criteria:

- Tests map to requirement IDs, task IDs, domain concepts, and acceptance criteria.
- MVP flows pass.
- Failure paths are tested.
- Validation report shows passed, failed, skipped, risks, and blockers.

Gate rule:

- Do not proceed to release if validation blockers remain unresolved or unaccepted.

Prepares next stage by creating release confidence.

### Stage 12: Release and Deployment

Objective: make the product safely deployable.

Inputs:

- Validation report.
- Architecture.
- Operations constraints.
- Evidence and proof packs.

Outputs:

- Deployment architecture.
- Environment definitions.
- Release process.
- Rollback plan.
- Secrets management.
- Production checklist.

Required artifacts:

- `wiki/deployment/deployment-architecture.md`.
- `wiki/deployment/environments.md`.
- `wiki/deployment/release-process.md`.
- `wiki/deployment/rollback-plan.md`.
- `wiki/deployment/secrets-management.md`.
- `wiki/deployment/production-checklist.md`.
- `wiki/reports/proof-packs/*.md`.
- `wiki/reports/releases/*.md`.

Decisions:

- Deployment path.
- Environment separation.
- Rollback strategy.
- Secrets handling.
- Release approvals.

Acceptance criteria:

- Deployment path is documented and reproducible.
- Rollback exists.
- Secrets are not committed.
- Health checks, logs, and metrics exist where relevant.
- Production checklist passes or has accepted exceptions.

Gate rule:

- Do not mark release ready without validation evidence, deployment plan, rollback plan, and accepted risk state.
- `GATE-RELEASE` / `python3 tools/echel.py readiness --stage release` checks validation blockers, deployment artifacts, rollback, production checklist rows, registered evidence, and release risk mitigation or acceptance before any production-ready claim.

Prepares next stage by making the system operable.

### Stage 13: Operations and Evolution

Objective: keep the product alive and learning after launch.

Inputs:

- Released product.
- Operational signals.
- Incidents.
- Customer feedback.
- Metrics.

Outputs:

- Runbook.
- Observability model.
- Incident response.
- Backup and recovery.
- SLA/SLO.
- Change management.
- Evolution backlog.

Required artifacts:

- `wiki/operations/runbook.md`.
- `wiki/operations/observability.md`.
- `wiki/operations/incident-response.md`.
- `wiki/operations/backup-and-recovery.md`.
- `wiki/operations/sla-and-slo.md`.
- `wiki/operations/change-management.md`.
- `wiki/operations/evolution-backlog.md`.

Decisions:

- Operational responsibilities.
- Alert thresholds.
- Incident severity and escalation.
- Backup and recovery process.
- Change approval process.
- Evolution prioritization.

Acceptance criteria:

- Support team can operate the product.
- Incidents have runbooks.
- Metrics exist.
- Backup and recovery are tested where applicable.
- Evolution backlog is governed by evidence and strategy.

Gate rule:

- Post-release learning must feed new discoveries, decisions, risks, requirements, tasks, or roadmap updates.
- TASK-0037 establishes `wiki/operations/` as the required operations artifact surface before TASK-0038 automates incidents, RCA, customer feedback, roadmap changes, and strategy changes into product memory.
- TASK-0038 implements `python3 tools/echel.py learning add` as the routed learning command. It may create follow-up task packets, proposed ADRs, risks, assumptions, or strategy-change records, but product behavior changes still require an approved task packet and evidence.

Prepares the next lifecycle loop by turning operations into product intelligence.

### Stage 14: Governance and Integrity

Objective: keep the repository coherent as work evolves.

Inputs:

- All lifecycle artifacts.
- Code, tests, evidence, decisions, incidents, and operations records.

Outputs:

- Documentation governance.
- Architecture governance.
- ADR process.
- Traceability matrix.
- Quality gates.
- Repository integrity audit.
- Contradiction register and resolution tasks.

Required artifacts:

- `wiki/governance/documentation-governance.md`.
- `wiki/governance/architecture-governance.md`.
- `wiki/governance/adr-process.md`.
- `wiki/governance/traceability-model.md`.
- `wiki/governance/quality-gates.md`.
- `wiki/governance/repository-integrity-audit.md`.
- `wiki/governance/contradictions.md`.

Decisions:

- Source-of-truth rules.
- Duplication and deprecation rules.
- Review requirements.
- Release and quality gates.
- Architecture review process.
- Contradiction resolution ownership.

Acceptance criteria:

- Every requirement traces to code, tests, and evidence.
- Every major architecture decision has an ADR.
- Every task updates docs when behavior changes.
- No important behavior remains undocumented.
- Integrity audit reports missing, stale, or contradictory artifacts.

Gate rule:

- Governance failures must either block progress or produce explicit accepted exceptions.

Prepares every future stage by keeping the system trustworthy.

## AI-Agent Role Model

Echel functions as a virtual delivery team. Each role has bounded authority, a defined lifecycle stage, and a contract expressed as responsibilities, inputs, outputs, and forbidden actions. The product-memory role contract lives in `wiki/agents/role-model.md`; this methodology section mirrors the contract so the lifecycle rules and product memory stay aligned. Every role consumes the shared engineering contract in `wiki/engineering/development-workflow.md` instead of redefining its own operating rules; the contract governs how a bounded work item becomes a verified repository change.

Role summary:

| Role | Lifecycle Stage(s) |
| --- | --- |
| Founder Interviewer | Discovery |
| Business Analyst | Discovery, Canon |
| Product Manager | Canon, Strategy, Requirements |
| Strategy Analyst | Strategy |
| Domain Modeler | Domain |
| Solution Architect | Architecture |
| Delivery Planner | Roadmap, Execution |
| Implementation Agent | Implementation |
| QA Agent | Validation |
| Security Reviewer | Strategy, Architecture, Implementation, Release, Operations |
| Release Manager | Release |
| Operations Steward | Operations |
| Governance Auditor | Governance (all stages) |

### Founder Interviewer

- Responsibilities: Elicit discovery information from the founder or product owner; separate facts, assumptions, hypotheses, constraints, and open questions; keep the Product Discovery Specification honest and complete.
- Inputs: Raw product idea; founder interviews; market and domain signals; the discovery quality gate checklist.
- Outputs: A populated `wiki/discovery/product-discovery-spec.md`; `wiki/discovery/assumptions.md` entries; `wiki/discovery/research-plan.md`; open-question log.
- Forbidden actions: Must not create architecture, requirements, or implementation tasks. Must not invent business facts to fill gaps. Must not mark an assumption as a verified fact.

### Business Analyst

- Responsibilities: Convert discovery into problem analysis, workflows, pain points, requirements seeds, and business rules; expose ambiguity for clarification before it reaches downstream stages.
- Inputs: Product Discovery Specification; assumptions and research plan; founding interviews.
- Outputs: Problem analysis notes; workflow and pain-point mappings; requirements seeds; business-rule drafts; clarification requests for contradictory discovery content.
- Forbidden actions: Must not invent missing business facts. Must not author architecture or choose technology. Must not write code.

### Product Manager

- Responsibilities: Own product canon, scope, roadmap, acceptance criteria, and priority; keep MVP small and out-of-scope explicit; balance strategy intent against delivery reality.
- Inputs: Product Canon; strategy artifacts; requirements model; discovery and research signals.
- Outputs: Updated canon scope and priorities; MVP vs. later-phase scope decisions; acceptance-criteria ownership; roadmap inputs; descoping rationale.
- Forbidden actions: Must not expand MVP beyond validated discovery value. Must not treat assumptions as committed scope. Must not author architecture or implementation.

### Strategy Analyst

- Responsibilities: Define ICP, buyer model, market wedge, competition, pricing hypothesis, and PMF evidence; quantify where possible and mark uncertainty explicitly.
- Inputs: Product Canon; discovery buyer/user/operator fields; competitive and market research.
- Outputs: `wiki/strategy/` artifacts (ICP, buyer-user model, market wedge, competitive analysis, positioning, pricing, PMF evidence); continue/stop PMF evidence thresholds.
- Forbidden actions: Must mark unvalidated strategy as hypothesis. Must not present pricing or wedge as fact without evidence. Must not invent market data.

### Domain Modeler

- Responsibilities: Create ubiquitous language, bounded contexts, workflows, entities, aggregates, events, and policies that reflect requirements without leaking implementation.
- Inputs: Requirements model (functional, non-functional, acceptance criteria); product canon; strategy constraints.
- Outputs: `wiki/domain/` artifacts; requirement-to-domain coverage map; `DM-`, `BC-`, `AGG-`, `DE-`, `WF-`, `BR-###` IDs linked to requirements.
- Forbidden actions: Must not choose infrastructure or frameworks unless it is an explicit stated constraint. Must not invent requirements not traceable to upstream IDs. Must not write implementation code.

### Solution Architect

- Responsibilities: Create architecture from requirements and the domain model; preserve domain boundaries; record major decisions as ADRs; prepare deployment posture, data/security/observability models, and complexity rationale.
- Inputs: Domain model; requirements and NFRs; ADR history; non-negotiables.
- Outputs: `wiki/architecture/` artifacts; `ARCH-###` mappings; ADR suggestions; technology choices with justification; architecture readiness evidence.
- Forbidden actions: Must preserve domain boundaries. Must write ADRs for major decisions. Must not introduce unjustified complexity. Must not begin implementation except where a task explicitly asks for architecture work.

### Delivery Planner

- Responsibilities: Convert roadmap into executable phases and agent-ready tasks; keep each task small, scoped, and verifiable; define dependencies, definition of done, validation commands, and documentation obligations.
- Inputs: Roadmap artifacts; architecture readiness state; execution phase definitions.
- Outputs: `wiki/execution/` phase artifacts; `wiki/work/TASK-1xxx-*.md` records; `wiki/work/TASK_INDEX.md`; dependency and handoff notes.
- Forbidden actions: Must keep each task small, scoped, and verifiable. Must not generate tasks from roadmap prose without gated architecture readiness. Must not exceed phase scope or add unrequested work.

### Implementation Agent

- Responsibilities: Implement one work packet at a time; produce modified files, tests, verification output, evidence, and memory updates; preserve unrelated changes.
- Inputs: Selected `wiki/work/TASK-1xxx-*.md`; relevant canon, requirements, domain, and architecture sources; engineering workflow and coding standards.
- Outputs: Modified source files; tests for happy and failure paths; runnable proof; registered evidence; project-memory updates; handoff summary.
- Forbidden actions: Must not exceed task scope. Must not implement from raw ideas or conversational intent. Must not modify unrelated files. Must not close the task without evidence. Must not treat assumptions as facts.

### QA Agent

- Responsibilities: Map tests to requirements, tasks, domain concepts, and acceptance criteria; verify behavior against acceptance criteria; surface quality and coverage risk.
- Inputs: Requirements and acceptance criteria; implementation changes; domain model; task packet.
- Outputs: Test results (pass/fail/skip); coverage and traceability mapping; risk and blocker reports; validation evidence.
- Forbidden actions: Must report passed, failed, skipped, risks, and blockers honestly. Must not pass work that lacks acceptance-criteria evidence. Must not modify product behavior to make a test pass without a task.

### Security Reviewer

- Responsibilities: Review security-sensitive requirements, architecture, implementation, deployment, and operations; identify risks and required evidence; confirm non-negotiables are honored.
- Inputs: Requirements and NFRs; architecture security model; implementation diffs; deployment and operations plans; non-negotiables.
- Outputs: Security findings; risk register entries; required-evidence list; approval or blocking recommendation.
- Forbidden actions: Must identify risks and required evidence. Must not approve security-sensitive changes without evidence. Must not suppress findings to unblock a release.

### Release Manager

- Responsibilities: Prepare release readiness, proof packs, deployment checklist, rollback plan, and accepted exceptions; coordinate the release gate.
- Inputs: Proof packs; readiness reports; QA and security sign-off; architecture and operations artifacts; risk state.
- Outputs: Release summary; deployment checklist; rollback plan; accepted-exception log; release readiness report.
- Forbidden actions: Must not approve release without evidence and risk state. Must not drop rollback or verification steps. Must not accept exceptions that contradict non-negotiables silently.

### Operations Steward

- Responsibilities: Maintain runbooks, observability, incident response, backup/recovery, SLA/SLO, and evolution backlog; keep the product operable after release.
- Inputs: Release artifacts; architecture observability model; incident and support signals; operational metrics.
- Outputs: Runbooks; observability and SLO definitions; incident-response procedures; evolution backlog; operational learning records.
- Forbidden actions: Must feed operational learning back into product memory. Must not treat production incidents as one-off without a memory update. Must not bypass observability for speed.

### Governance Auditor

- Responsibilities: Run integrity checks across source truth, traceability, decisions, tasks, tests, evidence, and docs; confirm the system stays trustworthy across stages.
- Inputs: Source-of-truth hierarchy; traceability schema; gate policy; graph and memory state; lifecycle logs.
- Outputs: Integrity and contradiction reports; stale-artifact flags; governance exceptions; audit summaries.
- Forbidden actions: Must surface contradictions and stale artifacts. Must not silence findings to keep a stage green. Must not approve governance exceptions without recording them.

## Execution Safety Rules

Every implementation task must produce:

1. Modified files.
2. Runnable proof.
3. Tests or justified test exception.
4. Architecture compliance verification.
5. Updated project memory.

If one is missing, the task is not complete.

Agents must read the relevant upstream artifacts before implementation:

- Product Canon.
- Relevant requirements.
- Relevant domain model.
- Relevant architecture docs and ADRs.
- Current state.
- Task artifact.
- Work packet.

Agents must not:

- Implement from raw ideas.
- Treat assumptions as facts.
- Create architecture while implementing unless a task explicitly asks for architecture work.
- Modify unrelated files.
- Close tasks without evidence.
- Leave durable decisions only in chat.

## Canonical Lifecycle Playbooks

Canonical role execution prompts live under `prompts/playbooks/`. Tool-specific prompt packs must render from these playbooks and may add only tool runtime style.

Required playbooks:

- `discover.md`
- `canon.md`
- `strategy.md`
- `requirements.md`
- `domain.md`
- `architecture.md`
- `roadmap.md`
- `execute.md`
- `validate.md`
- `release.md`
- `operate.md`
- `govern.md`

Every playbook must preserve objective, primary role, required inputs, required outputs, guardrails, and canonical prompt text. The implementation playbook and tool-specific implementation prompts must enforce that no product implementation code is written before an approved `wiki/work/TASK-*.md` task packet exists.

## Agent Handoff Protocol

The canonical handoff protocol lives in `wiki/agents/handoff-protocol.md`. Every lifecycle stage output must include a Handoff Summary when it creates, changes, validates, releases, operates, or governs product memory.

Every Handoff Summary must include:

- From role.
- To role.
- Lifecycle stage.
- Source artifacts.
- Changed artifacts.
- Decision summary.
- Assumptions.
- Risks.
- Unresolved questions.
- Evidence and verification.
- Stale or impacted upstream artifacts.
- Next-stage instructions.
- Do not proceed if.

Handoffs must preserve assumptions, risks, unresolved questions, and next-stage instructions. A receiving role must not proceed when the handoff names a blocked gate, missing approved task packet for implementation, missing evidence, stale upstream artifact, or role-model forbidden action.

## Stage Gate Semantics

Gate outcomes:

- `ready`: required inputs are present and consistent.
- `at risk`: non-blocking issues exist and need owner attention.
- `blocked`: required inputs are missing, stale, contradicted, or unverifiable.

Every gate result must include:

- Stage name.
- Checked artifacts.
- Missing or stale inputs.
- Contradictions.
- Required remediation.
- Next permitted action.

Backward transitions are allowed when new evidence invalidates upstream assumptions, but they require a decision, contradiction, incident, RCA, or owner update artifact.

The deterministic stage schema is defined in `schema/lifecycle-stage.schema.md`. That schema is the implementation-facing contract for stage IDs, required artifacts, transition rules, gate conditions, and blocking rules.

## Documentation Synchronization Rules

After every meaningful change:

- Update affected product memory.
- Update affected operating docs.
- Record actual architectural decisions.
- Update task status and dependencies when scope or order changes.
- Refresh generated reports when they are part of the change.
- Append `wiki/log.md`.
- Run relevant verification commands.

Documentation is not secondary. In Echel, documentation, code, graph, tasks, tests, and evidence are one operating system.

## TASK-0001 Scope Boundary

This document defines the vNext methodology contract. It intentionally does not implement lifecycle schemas, commands, graph upgrades, cockpit changes, or templates. Those are downstream tasks that must use this contract as their source of truth.
