# Greenfield reference journey

## Control

- Journey version: 1
- Product version: Echel 2
- Status: accepted
- Authority: Echel maintainers
- Last reviewed: 2026-07-14
- Depends on: [Echel 2 product contract](product-contract.md)
- Uses: [Echel 2 ubiquitous language](ubiquitous-language.md)

This journey is the reproducible greenfield scenario for product design, implementation, usability evaluation, and the Echel 2 benchmark. It specifies observable behavior without requiring a particular UI or prematurely fixing the storage schema.

## Scenario and measurable outcome

An independent builder starts with this raw idea:

> Help a small volunteer group coordinate recurring food-bank collection shifts without relying on spreadsheets and message threads.

The journey succeeds when the builder uses Echel to turn that idea into a running, verified MVP increment, executed through Hermes, while preserving a traceable and progressively matured chain from problem evidence to operational learning.

The reference MVP is deliberately narrow: a coordinator creates a collection shift with capacity, a volunteer claims an available place, and both can see the resulting assignment. Authentication, notifications, payments, route optimization, native applications, multi-tenancy, and production-scale infrastructure are outside this scenario unless discovery demonstrates that one is essential to the tested problem.

This is a benchmark scenario, not a claim that the example is a viable business. Discovery may invalidate it. A correct Echel outcome may be to stop, narrow, or run a cheaper experiment instead of generating an application.

## Actors and authority

| Actor | Responsibility | Authority limit |
| --- | --- | --- |
| Builder | Supplies the idea, answers material questions, and owns product decisions | Must distinguish observed evidence from personal assumptions |
| Domain reviewer | Reviews food-bank workflow and terminology | Advises on domain truth; does not control implementation execution |
| Echel | Guides methodology, records product knowledge, explains maturity and next action, compiles task specifications, and evaluates evidence | Cannot invoke models or accept consequential decisions autonomously |
| Hermes | Executes bounded task specifications using selected models and tools | Cannot turn runtime output or memory into accepted product knowledge |
| Git and CI | Preserve code revisions and execute authoritative checks | Do not own product intent or interpret business outcomes |

One person may perform both builder and domain-reviewer duties for the reference run, but Echel must retain the distinct decisions and evidence.

## Starting inputs

Required at initialization:

1. A project name.
2. The raw idea above, or a semantically equivalent one.
3. The repository location.
4. The identity of the person authorized to accept product decisions.

Optional inputs include existing research, constraints, preferred technologies, and an available domain reviewer. Missing optional inputs remain unknown; Echel must not invent them or create placeholder documents for future stages.

Invalid initialization inputs are an empty idea, an inaccessible or conflicting repository location, a secret embedded in the idea, or no identifiable decision authority. Echel must reject or request correction with an actionable explanation and leave no partially initialized canonical state.

## Progression contract

The stages below define necessary decisions and observable outputs, not a mandatory waterfall. Echel asks the smallest next question that resolves material uncertainty. The builder may revisit any earlier decision, and low-risk experiments may begin before every later stage exists.

| Step | Minimum input | Material decision | Canonical knowledge created or revised | Exit evidence |
| --- | --- | --- | --- | --- |
| 1. Initialize | Raw idea and authority | Is this idea clear enough to investigate? | Idea record with provenance and assumptions | Builder confirms faithful capture |
| 2. Define problem | Idea plus initial discovery | Who experiences what problem, in which context, and how is it observed? | Problem, affected actor, observations, assumptions, and unknowns | At least one credible observation or an explicit discovery experiment |
| 3. Frame vision and opportunity | Accepted problem knowledge | What improved outcome is worth pursuing, and which opportunity claims remain hypotheses? | Vision, desired outcomes, opportunity hypotheses, and non-goals | Builder can state value without asserting unsupported market facts |
| 4. Choose strategy | Vision plus highest-risk hypotheses | Which audience, value slice, and experiment should be attempted first? | Target user, strategic choice, success signal, scope, and stop conditions | A bounded choice and its alternatives are recorded |
| 5. Specify requirements | Strategy and scenario evidence | What behavior must the first increment demonstrate? | User outcomes, acceptance conditions, constraints, and exclusions | Requirements are testable and trace to strategy |
| 6. Model the domain | Requirements and domain review | Which concepts and rules are necessary to describe the selected behavior? | Minimal domain terms, relationships, invariants, and unresolved questions | Domain reviewer accepts or disputes each consequential rule |
| 7. Select architecture | Requirements, domain, and repository constraints | What is the simplest architecture sufficient for this increment? | Decision with alternatives, boundaries, quality constraints, and reversal cost | Architecture covers requirements without unused extension points |
| 8. Plan outcomes | Accepted architecture and risks | In what order can the largest uncertainties and dependencies be resolved? | Outcome roadmap, first phase, dependencies, and phase evidence | First phase is independently evaluable |
| 9. Prepare executable work | Phase outcome and repository state | What bounded change can one run implement and verify? | Work items, then immutable task specifications and context bundles | Each task is implementable without reconstructing upstream intent |
| 10. Implement through Hermes | Task specification, context bundle, permissions | Is execution authorized, and what result should be retained? | Run reference, events, external Git references, findings, proposals, and evidence | Runtime completion is normalized; no agent output self-approves |
| 11. Verify and review | Acceptance conditions and evidence | Does the increment satisfy intent and policy? | Verification evidence and review decision | All conditions pass or failures return to work with explanations |
| 12. Release and deploy | Accepted increment and release policy | Is this evidence sufficient for the target environment? | Release and deployment references, approval, and known risks | External systems report an attributable outcome |
| 13. Learn and evolve | Usage, feedback, incidents, and prior knowledge | What earlier knowledge is supported, challenged, or stale? | Operational findings and approved proposals for backward revision | Impact is visible and an authorized person resolves it |

## Required decision trail

The scenario must preserve at least this sparse traceability chain:

```text
problem observation
  → strategic outcome
  → MVP requirement
  → domain rule
  → architecture decision
  → phase outcome
  → work item
  → immutable task specification
  → Git/CI evidence
  → review decision
  → operational finding
```

Every connection must state why it exists. Echel must not manufacture a complete graph, duplicate the same truth in multiple authoritative documents, or treat generated navigation as canonical knowledge.

## Reference decisions and expected evolution

These are benchmark expectations, not initialization defaults:

- Discovery should identify the coordinator and volunteer separately and test whether missed or overbooked shifts are a real recurring problem.
- The first strategy should favor one organization and one coordination workflow over a general volunteer-management platform.
- The minimal domain is expected to need `Volunteer`, `Shift`, `Capacity`, and `Assignment`; additional concepts require a current rule or use case.
- A modular monolith or comparably simple deployable is preferred unless recorded constraints disqualify it.
- The first implementation task should be a vertical slice with executable acceptance evidence, not infrastructure built for hypothetical scale.

If evidence leads elsewhere, the run remains valid when the divergence and rationale are recorded. Tests must evaluate methodology behavior, not force these example answers.

## Failure, interruption, and recovery paths

| Condition | Required Echel behavior | Recovery evidence |
| --- | --- | --- |
| Idea is vague or solution-first | Ask one material clarification and preserve the original idea | Revised problem proposal retains provenance to the input |
| User states an unsupported claim as fact | Record it as an assumption or hypothesis and explain why | Evidence and authorized acceptance are required to change its state |
| Discovery contradicts the problem | Surface impact; offer revise, experiment, or stop | Decision and affected relationships are recorded |
| User skips a stage | Permit it when the next decision has sufficient maturity; explain risk otherwise | Maturity explanation identifies missing knowledge, not missing documents |
| User changes an accepted upstream decision | Mark impacted downstream knowledge and task specifications stale | Recompilation occurs only after explicit resolution |
| Hermes is unavailable | Preserve useful planning and emit a portable task specification | A later runtime can execute without loss of task meaning |
| Hermes is interrupted or times out | Retain run events and partial external references without accepting completion | Resume or retry creates a distinct attempt with known prior state |
| Agent proposes out-of-scope work | Return it as a finding or proposal, not an automatic mutation | Builder accepts, rejects, or defers it explicitly |
| Tool permission is denied | Stop the affected action and explain the minimum permission or alternative | No unauthorized side effect; a new authorized attempt is traceable |
| Verification fails | Keep the work unaccepted and relate failure evidence to conditions | Corrective work receives only relevant failure context |
| Deployment fails | Preserve external outcome evidence and open an operational finding | Recovery or rollback result is referenced without rewriting intent |
| Repository or knowledge revision is stale | Reject the mutation and show the conflicting revision | User rebases the proposal or deliberately supersedes it |
| Secret or sensitive value is supplied | Redact and reject persistence in product records or context bundles | Safe replacement reference is used; absence is verified |

## Benchmark observations

Each reference run records the following without inventing target thresholds before E2-007:

1. Time and number of interactions from raw idea to an accepted, testable problem.
2. Number of questions asked, split into material, deferred, and unnecessary after review.
3. Number of canonical records created at each lifecycle step.
4. Assumptions later confirmed, rejected, or left unresolved.
5. Trace coverage from acceptance conditions to upstream intent and downstream evidence.
6. Context precision: included context judged necessary versus irrelevant or missing.
7. Task acceptance on first review, rework count, and review defects.
8. Runtime/model changes made without loss of task meaning.
9. Time to understand current state and identify the next action for a new contributor.
10. Operational findings that cause visible backward impact and approved knowledge revision.

The benchmark must retain raw measurements and reviewer rationale. Artifact count is a diagnostic, never a success measure by itself.

## Acceptance checklist for a completed journey

- Initialization created only the minimum canonical state and no future-stage skeletons.
- Observations, inferences, assumptions, hypotheses, facts, decisions, and evidence remained distinguishable.
- Each stage added knowledge because a current decision required it.
- Both progress and backward revision were explainable.
- The MVP remained bounded to the selected problem and strategy.
- Every runtime invocation used an immutable task specification and explainable context bundle.
- Hermes memory and output never became product truth without Echel policy and authorized review.
- Verification connected implementation evidence to acceptance conditions and upstream intent.
- The repository could be understood and evolved after the original runtime session ended.
- All benchmark observations were captured with reproducible source references.

## Non-goals

This journey does not prescribe screen design, storage schemas, a programming language, a model provider, hosted infrastructure, fixed agent personas, exhaustive lifecycle documentation, or automatic product viability. It does not replace the brownfield reference journey. Shared terminology and task/runtime contracts must converge, while the evidence used to establish initial knowledge differs.

## Review decision

Reviewers should approve this journey when its inputs, decisions, progressive outputs, authority boundaries, failure and recovery behavior, and measurements are sufficient for two independent implementations to produce comparable evidence. Requested changes must identify the ambiguous behavior or missing measurable outcome rather than add speculative features.
