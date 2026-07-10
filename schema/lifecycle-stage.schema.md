---
type: schema
status: active
---
# Lifecycle Stage Schema

This schema defines the deterministic lifecycle contract for Echel vNext stages. It refines the methodology in `docs/development/methodology.md` into stage IDs, required artifacts, transition rules, gate conditions, blocking rules, and backward-transition reason requirements.

## Purpose

Lifecycle stages prevent AI agents from skipping product understanding and writing code from vague intent. A stage is ready only when its required inputs exist, its required artifacts satisfy the gate conditions, and unresolved blockers are either fixed or explicitly accepted by the product owner.

## Stage Object

Each lifecycle stage is represented conceptually as:

```json
{
  "id": "discovery",
  "order": 1,
  "title": "Product Discovery",
  "objective": "Convert raw idea into a Product Discovery Specification.",
  "required_inputs": [],
  "required_artifacts": [],
  "gate_conditions": [],
  "allowed_next": [],
  "allowed_previous": [],
  "blocking_rules": [],
  "reason_artifacts_for_backward_transition": []
}
```

Required fields:

- `id`: stable lowercase stage identifier.
- `order`: integer lifecycle order.
- `title`: human-readable stage name.
- `objective`: reason the stage exists.
- `required_inputs`: upstream stage outputs or owner inputs needed before evaluation.
- `required_artifacts`: canonical files or artifact classes that must exist.
- `gate_conditions`: deterministic checks that decide readiness.
- `allowed_next`: stage IDs that may follow when the gate is ready.
- `allowed_previous`: stage IDs that may be revisited with a reason artifact.
- `blocking_rules`: conditions that force the stage status to `blocked`.
- `reason_artifacts_for_backward_transition`: accepted artifact types for revisiting earlier stages.

## Canonical Stage IDs

| Order | ID | Title |
| --- | --- | --- |
| 0 | `repository-initialization` | Repository Initialization |
| 1 | `discovery` | Product Discovery |
| 2 | `canon` | Product Canon |
| 3 | `strategy` | Product Strategy |
| 4 | `requirements` | Requirements |
| 5 | `domain` | Domain Model |
| 6 | `architecture` | Architecture |
| 7 | `roadmap` | Roadmap |
| 8 | `execution-planning` | Execution Planning |
| 9 | `repository-factory` | Repository Factory |
| 10 | `implementation` | Implementation |
| 11 | `validation` | Validation |
| 12 | `release-deployment` | Release And Deployment |
| 13 | `operations-evolution` | Operations And Evolution |
| 14 | `governance-integrity` | Governance And Integrity |

## Readiness Status

Stage evaluation returns exactly one status:

- `ready`: required artifacts exist, gate conditions pass, and no blockers remain.
- `at risk`: required artifacts exist, but warnings or accepted exceptions need owner attention.
- `blocked`: required artifacts are missing, stale, contradicted, or unverifiable.

Every evaluation result must include:

- stage ID
- checked artifacts
- status
- blockers
- warnings
- accepted exceptions
- next permitted action

## Transition Rules

- Forward transitions are allowed only when the current stage is `ready` or when the product owner explicitly accepts `at risk` warnings.
- A stage may not be skipped unless an accepted decision artifact explains why the skipped stage is not applicable.
- Backward transitions are allowed only with a reason artifact.
- A backward transition marks dependent downstream stages as stale until reevaluated.
- Implementation cannot begin until `execution-planning` and `repository-factory` are ready.
- Release cannot begin until validation is ready or accepted exceptions are documented.
- Operations and evolution must feed new signals back into discovery, canon, strategy, requirements, roadmap, tasks, risks, or decisions.

Accepted reason artifact types:

- `decision`
- `contradiction`
- `incident`
- `rca`
- `owner-update`
- `research-result`
- `accepted-exception`

## Stage Definitions

### repository-initialization

Objective: create the execution container and product memory boundary.

Required inputs:

- product name
- raw idea or existing repository path

Required artifacts:

- `README.md`
- `wiki/project.md`
- `wiki/log.md`
- `project.echel`

Gate conditions:

- product memory root is resolvable
- Echel Core path boundary is documented
- repository mode is known
- no product implementation has started from raw idea

Allowed next:

- `discovery`

Blocking rules:

- missing project configuration
- missing product memory root
- ambiguous repository ownership boundary

### discovery

Objective: convert raw idea into a Product Discovery Specification.

Required inputs:

- repository initialization
- founder or domain-expert intent
- raw references, notes, constraints, or existing repo context

Required artifacts:

- `wiki/discovery/product-discovery-spec.md`
- `wiki/discovery/research-plan.md`
- `wiki/discovery/assumptions.md`

Gate conditions:

- problem is clearly defined
- buyer, user, and operator are separated
- current workflow is documented
- measurable business value exists
- non-goals are explicit
- constraints are documented
- success criteria are measurable
- major risks are listed
- assumptions are listed with confidence
- open questions are documented
- research plan exists
- MVP scope is defined

Allowed next:

- `canon`

Blocking rules:

- missing Product Discovery Specification
- no buyer or user model
- assumptions treated as facts
- missing scope or non-goals
- unresolved high-impact question with no owner decision

### canon

Objective: define stable product truth.

Required inputs:

- ready discovery stage
- resolved or accepted discovery questions

Required artifacts:

- `wiki/canon/product-canon.md`
- `wiki/canon/vision.md`
- `wiki/canon/product-principles.md`
- `wiki/canon/non-negotiables.md`

Gate conditions:

- canon states what the product is and is not
- canon states why the product exists
- canon identifies who the product serves
- canon explains why customers would pay or adopt
- non-negotiable constraints are explicit
- canon references discovery IDs

Allowed next:

- `strategy`

Allowed previous:

- `discovery`

Blocking rules:

- canon contradicts discovery without a reason artifact
- product identity is vague
- non-negotiables missing

### strategy

Objective: turn canon into a market wedge and business plan.

Required inputs:

- ready canon stage
- buyer and user model
- competitive alternatives

Required artifacts:

- `wiki/strategy/icp.md`
- `wiki/strategy/buyer-user-model.md`
- `wiki/strategy/market-wedge.md`
- `wiki/strategy/competitive-analysis.md`
- `wiki/strategy/positioning.md`
- `wiki/strategy/pricing-and-packaging.md`
- `wiki/strategy/pmf-evidence.md`

Gate conditions:

- first ICP is specific
- buyer is not confused with user
- first wedge is explicit
- primary alternatives are listed
- switching cost and adoption blockers are visible
- pricing is marked as hypothesis unless validated
- PMF evidence includes continue and stop criteria

Allowed next:

- `requirements`

Allowed previous:

- `canon`
- `discovery`

Blocking rules:

- vague ICP
- missing economic buyer
- missing PMF evidence
- unvalidated pricing treated as fact

### requirements

Objective: convert strategy into testable build scope.

Required inputs:

- ready strategy stage
- canon constraints
- discovery business rules

Required artifacts:

- `wiki/requirements/product-requirements.md`
- `wiki/requirements/functional-requirements.md`
- `wiki/requirements/non-functional-requirements.md`
- `wiki/requirements/mvp-scope.md`
- `wiki/requirements/out-of-scope.md`
- `wiki/requirements/acceptance-criteria.md`

Gate conditions:

- every MVP requirement has an ID
- every MVP requirement is testable
- acceptance criteria exist
- dependencies are visible
- risks are linked
- out-of-scope is explicit
- non-functional requirements exist where needed

Allowed next:

- `domain`

Allowed previous:

- `strategy`
- `canon`
- `discovery`

Blocking rules:

- vague requirements
- missing acceptance criteria
- unbounded MVP scope
- missing out-of-scope

### domain

Objective: define product language and business boundaries before architecture.

Required inputs:

- ready requirements stage
- business rules
- workflows

Required artifacts:

- `wiki/domain/domain-overview.md`
- `wiki/domain/ubiquitous-language.md`
- `wiki/domain/bounded-contexts.md`
- `wiki/domain/entities.md`
- `wiki/domain/aggregates.md`
- `wiki/domain/domain-events.md`
- `wiki/domain/workflows.md`
- `wiki/domain/policies-and-rules.md`

Gate conditions:

- every requirement maps to at least one domain concept
- important terms have one definition
- bounded contexts have responsibilities and forbidden responsibilities
- workflows and policies are documented
- technology decisions are absent unless marked as constraints
- generated domain IDs are present in the product graph
- every referenced domain concept, context, aggregate, event, workflow, and rule ID is defined

Allowed next:

- `architecture`

Allowed previous:

- `requirements`
- `strategy`

Blocking rules:

- undefined core terms
- duplicate meanings for one concept
- unmapped MVP requirement
- technology leakage into domain model

### architecture

Objective: decide how the system will be built while preserving domain boundaries.

Required inputs:

- ready domain stage
- requirements
- non-functional expectations
- constraints

Required artifacts:

- `wiki/architecture/overview.md`
- `wiki/architecture/context-map.md`
- `wiki/architecture/component-architecture.md`
- `wiki/architecture/data-architecture.md`
- `wiki/architecture/api-architecture.md`
- `wiki/architecture/event-architecture.md`
- `wiki/architecture/workflow-architecture.md`
- `wiki/architecture/security-architecture.md`
- `wiki/architecture/observability-architecture.md`
- `wiki/decisions/ADR-*.md`

Gate conditions:

- system shape is stated
- deployment model or deployment posture is stated
- data strategy is stated
- API or integration strategy is stated when applicable
- security model is stated
- observability model is stated
- major decisions have ADRs
- architecture maps to requirements and domain contexts
- complexity is justified
- generated architecture graph nodes and mapping edges exist for generated `ARCH-9xx` rows

Runtime gate:

- `GATE-ARCHITECTURE` evaluates these conditions through `echel readiness --stage architecture`.

Allowed next:

- `roadmap`

Allowed previous:

- `domain`
- `requirements`

Blocking rules:

- missing ADR for major choice
- architecture violates domain boundary
- missing security or data strategy
- unjustified distributed complexity

### roadmap

Objective: turn architecture into phased delivery.

Required inputs:

- ready architecture stage
- MVP scope
- risks and constraints

Required artifacts:

- `wiki/roadmap/master-roadmap.md`
- `wiki/roadmap/mvp-roadmap.md`
- `wiki/roadmap/architecture-roadmap.md`
- `wiki/roadmap/engineering-roadmap.md`
- `wiki/roadmap/release-plan.md`

Gate conditions:

- roadmap produces usable product early
- phases have objectives and outputs
- dependencies are explicit
- demo scenario exists per phase
- phase exit gates are defined

Allowed next:

- `execution-planning`

Allowed previous:

- `architecture`
- `requirements`

Blocking rules:

- phase depends on undefined work
- no MVP delivery path
- missing phase exit gates

### execution-planning

Objective: create phases and tasks that AI agents can execute safely.

Required inputs:

- ready roadmap stage
- architecture
- requirements
- domain model

Required artifacts:

- `wiki/execution/phase-0-foundation.md`
- `wiki/execution/phase-1-mvp.md`
- `wiki/execution/phase-2-hardening.md`
- `wiki/execution/phase-3-production.md`
- `wiki/execution/phase-4-evolution.md`
- `wiki/work/TASK-*.md`
- `wiki/work/TASK_INDEX.md`

Gate conditions:

- `python3 tools/echel.py execution-tasks` has run after architecture readiness
- every phase has task list and dependencies
- every task has objective, business reason, scope, out-of-scope, acceptance criteria, tests, validation command, rollback notes, documentation updates, and definition of done
- tasks are small enough for one AI coding session
- work packets can be generated

Allowed next:

- `repository-factory`
- `implementation`

Allowed previous:

- `roadmap`
- `architecture`

Blocking rules:

- vague task
- task mixes unrelated concerns
- missing verification command
- missing documentation update scope

### repository-factory

Objective: create or update the executable repository baseline.

Required inputs:

- ready execution-planning stage
- architecture
- engineering constraints

Required artifacts:

- `wiki/engineering/repository-structure.md`
- `wiki/engineering/coding-standards.md`
- `wiki/engineering/development-workflow.md`
- `wiki/engineering/configuration-strategy.md`
- `wiki/engineering/local-development.md`

Gate conditions:

- repository structure matches architecture
- local boot or health check command exists
- test command exists
- lint or quality command exists
- environment/configuration strategy exists

Allowed next:

- `implementation`

Allowed previous:

- `execution-planning`
- `architecture`

Blocking rules:

- no executable baseline
- no test command
- missing configuration strategy

### implementation

Objective: build one small verified task at a time.

Required inputs:

- ready execution-planning stage
- ready repository-factory stage for code work
- task artifact
- work packet

Required artifacts:

- modified source files
- tests or accepted test exception
- `wiki/reports/reviews/*.md`
- registered evidence
- updated task and product memory

Gate conditions:

- task scope is satisfied
- validation commands pass
- architecture compliance is checked
- evidence is registered
- affected memory is updated

Allowed next:

- `validation`
- `execution-planning`

Allowed previous:

- `execution-planning`
- `architecture`
- `requirements`

Blocking rules:

- implementation from raw idea
- no work packet
- no runnable proof
- no evidence
- unrelated file changes
- architecture decision without ADR

### validation

Objective: prove the product works against requirements and acceptance criteria.

Required inputs:

- implemented behavior
- requirements
- domain model
- tasks
- evidence

Required artifacts:

- `wiki/validation/test-strategy.md`
- `wiki/validation/acceptance-tests.md`
- `wiki/validation/integration-tests.md`
- `wiki/validation/e2e-tests.md`
- `wiki/validation/security-tests.md`
- `wiki/validation/performance-tests.md`
- `wiki/validation/validation-report.md`

Gate conditions:

- tests map to requirements, tasks, domain concepts, and acceptance criteria
- MVP flows pass
- failure paths are tested
- validation report lists passed, failed, skipped, risks, and blockers

Allowed next:

- `release-deployment`
- `implementation`

Allowed previous:

- `implementation`
- `requirements`

Blocking rules:

- failed critical validation
- missing validation report
- unmapped test coverage for MVP requirement
- unresolved production blocker

### release-deployment

Objective: make the product safely deployable.

Required inputs:

- ready validation stage
- architecture
- proof pack
- risk state

Required artifacts:

- `wiki/deployment/deployment-architecture.md`
- `wiki/deployment/environments.md`
- `wiki/deployment/release-process.md`
- `wiki/deployment/rollback-plan.md`
- `wiki/deployment/secrets-management.md`
- `wiki/deployment/production-checklist.md`
- `wiki/reports/proof-packs/*.md`
- `wiki/reports/releases/*.md`

Gate conditions:

- deployment path is documented
- rollback plan exists
- secrets strategy exists
- environments are separated where applicable
- production checklist passes or exceptions are accepted
- release risks are mitigated or accepted

Allowed next:

- `operations-evolution`

Allowed previous:

- `validation`
- `architecture`

Blocking rules:

- no rollback plan
- no proof pack
- unresolved release blocker
- secrets committed or unmanaged

### operations-evolution

Objective: operate the product and turn feedback into product intelligence.

Required inputs:

- release state
- operational signals
- incidents
- customer feedback
- metrics

Required artifacts:

- `wiki/operations/runbook.md`
- `wiki/operations/observability.md`
- `wiki/operations/incident-response.md`
- `wiki/operations/backup-and-recovery.md`
- `wiki/operations/sla-and-slo.md`
- `wiki/operations/change-management.md`
- `wiki/operations/evolution-backlog.md`

Gate conditions:

- support responsibilities are clear
- incident severity and escalation are defined
- observability expectations are documented
- backup and recovery are documented where applicable
- evolution backlog is governed by evidence and strategy

Allowed next:

- `governance-integrity`
- `discovery`
- `strategy`
- `requirements`
- `roadmap`
- `execution-planning`

Allowed previous:

- `release-deployment`

Blocking rules:

- no runbook
- no incident response path
- operational learning not captured

### governance-integrity

Objective: keep the repository coherent as work evolves.

Required inputs:

- all lifecycle artifacts
- code, tests, evidence, decisions, incidents, and operations records

Required artifacts:

- `wiki/governance/documentation-governance.md`
- `wiki/governance/architecture-governance.md`
- `wiki/governance/adr-process.md`
- `wiki/governance/traceability-model.md`
- `wiki/governance/quality-gates.md`
- `wiki/governance/repository-integrity-audit.md`

Gate conditions:

- source-of-truth hierarchy is explicit
- duplication and deprecation rules exist
- every major architecture decision has ADR coverage
- every MVP requirement traces to code, tests, and evidence
- stale or contradictory artifacts are reported

Allowed next:

- any earlier stage with a reason artifact

Allowed previous:

- any earlier stage

Blocking rules:

- broken critical traceability
- undocumented major behavior
- unresolved contradiction without owner decision
- missing required evidence for closed work

## Deterministic Evaluation Rules

A stage evaluator must:

1. Resolve `WIKI_ROOT`.
2. Check required artifacts for existence.
3. Evaluate gate conditions from declared artifacts only.
4. Report missing inputs as blockers.
5. Report contradictions as blockers unless accepted.
6. Report incomplete optional improvements as warnings.
7. Never call external services during gate evaluation unless their output has already been captured as evidence.
8. Return the same result for the same repository state.

## Relationship To Other Schemas

- `schema/EXECUTION.md` defines task/story/incident lifecycle behavior.
- `schema/readiness.schema.md` defines milestone and release readiness report shape.
- `schema/product-graph.schema.md` defines the relationship graph that will later include lifecycle stage nodes and edges.
- `docs/development/methodology.md` remains the narrative source of truth; this schema is the deterministic stage contract.
