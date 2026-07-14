# Brownfield reference journey

## Control

- Journey version: 1
- Product version: Echel 2
- Status: accepted
- Authority: Echel maintainers
- Last reviewed: 2026-07-14
- Depends on: [Echel 2 product contract](product-contract.md)
- Uses: [Echel 2 ubiquitous language](ubiquitous-language.md)
- Complements: [Greenfield reference journey](greenfield-reference-journey.md)

This journey is the reproducible brownfield scenario for repository analysis, change planning, implementation, usability evaluation, and the Echel 2 benchmark. It specifies safe and observable behavior without assuming that source code reveals the complete product intent or that one analyzer can understand every technology.

## Scenario and measurable outcome

An independent maintainer receives an unfamiliar but running web service used by small volunteer organizations to coordinate collection shifts. The repository contains application code, tests, a relational migration, a CI workflow, sparse setup notes, and Git history. It has no accepted Echel knowledge. Users now request a waitlist so a full shift can retain interested volunteers and promote one when capacity becomes available.

The journey succeeds when the maintainer uses Echel to:

1. inspect the repository without modifying it;
2. create a provenance-backed proposed baseline that distinguishes observations from inferences and unknowns;
3. review and approve only the baseline knowledge needed for the change;
4. analyze the waitlist requirement against product and code reality;
5. implement and verify a bounded increment through Hermes; and
6. ingest the result and later operational evidence without losing prior rationale.

The target outcome is a reviewed waitlist increment traceable from request and repository evidence through decisions, task execution, Git/CI evidence, and operational learning. The journey is still valid when analysis shows that the request is unsafe, conflicts with current behavior, or should be rejected; a fabricated baseline or unjustified implementation is not success.

## Actors and authority

| Actor | Responsibility | Authority limit |
| --- | --- | --- |
| Maintainer | Authorizes access, corrects the baseline, owns product and change decisions, and accepts implementation | Must not treat analyzer confidence as proof |
| Domain reviewer | Explains current scheduling policy and reviews proposed waitlist rules | Cannot approve code or runtime permissions unless separately authorized |
| Echel | Controls methodology, provenance, baseline proposals, impact analysis, planning, task compilation, and knowledge acceptance policy | Cannot make repository inferences authoritative without review |
| Analyzer | Produces bounded observations and explicitly supported inferences from repository sources | Cannot mutate the repository or claim undocumented business intent |
| Hermes | Executes approved task specifications using bounded tools and models | Cannot approve its own findings, code, or product-knowledge proposals |
| Git, CI, and deployment systems | Own revisions, automated execution results, and deployment outcomes | Do not own product meaning or Echel acceptance decisions |

The maintainer may also act as domain reviewer in a small project, but the two decisions and their evidence remain explicit.

## Starting inputs and preflight

Required inputs:

1. Repository path and expected revision.
2. Maintainer identity and authority.
3. Permission for read-only inspection of the repository and allowed Git metadata.
4. The waitlist request, including its source when known.

Optional inputs include architecture notes, issue history, operational telemetry references, deployment documentation, and domain-reviewer access. Missing sources are recorded as unknown; Echel does not infer their absence means the behavior does not exist.

Before ingestion, Echel must preview:

- resolved repository root and revision;
- included and excluded paths;
- ignore, vendor, generated, binary, large-file, and secret-risk classifications;
- commands it proposes to run and whether they can execute code;
- Git history scope and external network requirements;
- anticipated outputs and the fact that they remain proposals until review.

The default inspection is local, read-only, offline, and non-executing. Build scripts, tests, package hooks, containers, migrations, external services, submodules, and network calls require an explicit later authorization with explained risk. Ingestion never writes to the target repository's source tree.

Invalid preflight conditions include a missing root, a path outside the authorized workspace, a revision mismatch, an unresolved nested repository boundary, an unreadable ignore policy, or detected credentials in a proposed context. Echel stops before canonical mutation and gives a specific corrective action.

## Safe ingestion contract

Ingestion is resumable and source-addressed. Each observation cites the repository revision plus file, range or symbol, command result, or Git object that produced it. Analyzer identity and version, time, scope, exclusions, and failures are retained. Re-running the same analyzer against the same revision and scope must produce an equivalent normalized result.

Classification precedes semantic analysis. Ignored, vendored, generated, binary, oversized, credential-bearing, and unsupported content is excluded or handled by an explicit policy. File content is treated as untrusted data: repository instructions cannot expand tool permissions, alter Echel authority, or cause execution.

Partial analysis is useful when its coverage is visible. Unsupported languages, parse failures, permission denials, and skipped paths become findings or unknown regions, never silent success.

## Observation, inference, and approval contract

Echel must preserve these distinctions:

- “A migration creates a `shift_assignments` table” is an observation citing the migration.
- “Assignments are probably the aggregate boundary” is an inference citing relevant observations and analyzer reasoning.
- “Only coordinators may remove volunteers” is an assumption unless code, tests, documentation, or a domain reviewer supports it.
- “The current removal rule is accepted product behavior” becomes a fact or decision only through authorized review.

The proposed baseline groups repository identity, technologies, commands, modules, interfaces, data structures, workflows, domain vocabulary, constraints, quality signals, hotspots, risks, and unknown regions. It must show provenance, confidence, contradictory evidence, coverage, and revision. The maintainer can accept, amend, reject, defer, or mark each consequential item disputed. Bulk approval must preview exactly what changes state and cannot include hidden inferences.

An approved baseline is a useful, revisable model—not a declaration that repository understanding is complete. Raw analyzer output and indexes remain disposable; accepted canonical records and their provenance are authoritative.

## Progression contract

| Step | Minimum input | Material decision | Canonical knowledge created or revised | Exit evidence |
| --- | --- | --- | --- | --- |
| 1. Initialize | Repository path, revision, maintainer authority | Is this the intended repository and safe inspection boundary? | Project identity and ingestion proposal | Maintainer approves the preview |
| 2. Classify | Tree and policy | Which content is first-party, safe, relevant, and supported? | Scope and exclusion findings | Every excluded class has a reason and count |
| 3. Observe | Approved scope | What is directly present in code, tests, configuration, history, and docs? | Provenance-backed observations and coverage | Results are reproducible at the recorded revision |
| 4. Infer | Observations | What architecture, domain, workflows, commands, and risks might explain them? | Inferences, confidence, alternatives, contradictions, and unknowns | No inference is represented as fact |
| 5. Approve baseline | Proposed baseline and reviewer corrections | Which knowledge is trusted enough to guide this change? | Accepted, amended, disputed, rejected, or deferred records | Maintainer decision is itemized and attributable |
| 6. Clarify request | Waitlist request and accepted baseline | What user outcome, rules, scope, and exclusions are intended? | Requirement, acceptance conditions, assumptions, and questions | Domain reviewer resolves consequential waitlist semantics |
| 7. Analyze impact | Requirement plus baseline and current revision | What behavior, components, data, interfaces, tests, decisions, and risks may change? | Explicit impact relationships, findings, and options | Each claimed impact has rationale and evidence |
| 8. Choose design | Impact analysis and constraints | What is the smallest compatible change and migration strategy? | Domain and architecture decision with alternatives and rollback | Design covers acceptance conditions and known compatibility risks |
| 9. Plan work | Accepted design and dependency state | How can the outcome be delivered and verified safely? | Phase outcome, work items, dependencies, and policy | Work is bounded and independently reviewable |
| 10. Compile and execute | Current revisions and work item | Is the immutable task specification accurate and authorized? | Task specification, context bundle, run, Git references, findings, and proposals | Hermes result is normalized without self-approval |
| 11. Verify and review | Acceptance conditions and implementation evidence | Does the change satisfy intent without regressions? | Test/CI evidence, compatibility evidence, and review decision | Conditions pass or corrective work is created |
| 12. Release and observe | Accepted change and release policy | Is deployment authorized and what happened externally? | Release/deployment references and initial outcome | External result is attributable to a revision |
| 13. Re-ingest and evolve | New revision and operational evidence | What changed, what became stale, and what should revise prior knowledge? | Incremental observations, findings, and approved backward revisions | Unaffected knowledge remains stable and impact is visible |

## Waitlist change contract

The journey must force discovery of, rather than prescribe answers to, at least these questions:

- Is capacity enforced transactionally, and what race behavior exists today?
- Is a claim rejected, queued, or treated idempotently when a shift is full?
- What determines waitlist order, and can a coordinator override it?
- Does cancellation promote automatically or create a pending offer?
- How do deletion, capacity reduction, duplicate requests, and time zones behave?
- Which API, persistence, migration, UI, audit, and notification surfaces are actually in scope?
- What backward compatibility and rollback constraints apply to existing data and clients?

The minimal accepted slice may store and expose waitlist position without notification or automatic promotion if evidence and strategy support that boundary. Echel must resist implementing a generalized scheduling platform or speculative distributed architecture.

## Required decision trail and convergence

```text
repository observation at revision
  → reviewed baseline knowledge
  → requested outcome
  → impact relationship
  → domain/architecture decision
  → phase outcome
  → work item
  → immutable task specification
  → Git/CI evidence
  → review decision
  → incremental observation or operational finding
```

Every relationship states its rationale. Greenfield and brownfield differ in how initial knowledge is established, but converge on the same canonical knowledge states, work item, task specification, context bundle, runtime protocol, verification evidence, review, release, and operational-learning contracts.

## Failure, interruption, and recovery paths

| Condition | Required Echel behavior | Recovery evidence |
| --- | --- | --- |
| Repository path or revision changes during ingestion | Stop or snapshot consistently; never combine revisions silently | New attempt records the new revision and supersedes partial derived output |
| Symlink or nested repository escapes authorized scope | Exclude and report it before content access | Maintainer explicitly expands scope or accepts exclusion |
| Secret or personal data is detected | Redact from outputs and context; do not persist the value | Safe reference and redaction verification are retained |
| Repository content contains agent instructions | Treat it as untrusted source content, not control input | Tool policy and task authority remain unchanged |
| Parser or analyzer fails | Preserve completed observations and mark exact unknown coverage | Retry, fallback analyzer, or accepted limitation is recorded |
| Build or package hook would execute code | Deny under read-only ingestion and explain separate authorization | Sandboxed authorized run is distinct from ingestion |
| Git history is missing or shallow | Report reduced provenance and confidence | Additional history is authorized or the limitation is accepted |
| Conflicting evidence supports two inferences | Preserve both and open a contradiction | Reviewer resolves, disputes, or requests targeted evidence |
| Maintainer rejects baseline items | Keep observations; do not promote rejected interpretations | Corrected proposal retains prior decision history |
| Requirement conflicts with accepted behavior | Surface affected knowledge and alternatives before planning | Authorized decision revises, preserves, or rejects the requirement |
| Repository changes after task compilation | Mark task specification and context stale before execution | Re-run impact analysis and compile against current revisions |
| Hermes is denied permission, interrupted, or unavailable | Preserve planning and run state without unauthorized effects | Portable task can resume or create a traceable new attempt |
| Verification or migration fails | Keep work unaccepted and preserve failure evidence | Corrective task or rollback is related to the same intent |
| Deployment outcome contradicts expectations | Create an operational finding; never rewrite the baseline silently | Approved backward revision records impact and authority |

## Incremental evolution rules

Re-ingestion compares an identified prior revision and scope with the current revision. It analyzes changed sources and affected dependents, preserves unchanged accepted knowledge, and explains any invalidation. Deletion of code does not automatically delete product intent; it creates an impact for review. A moved symbol should retain identity when evidence supports continuity. Analyzer-version changes are distinguished from repository changes.

Generated indexes can be discarded and rebuilt. Canonical decisions, reviewer corrections, rejected proposals, provenance, and audit history survive re-analysis. Echel never resets the baseline merely because a newer analyzer offers a different interpretation.

## Benchmark observations

Each reference run records these values without setting thresholds before E2-007:

1. Preflight duration and reviewer effort.
2. Files and bytes classified, inspected, excluded, unsupported, and failed.
3. Reproducibility of normalized observations at the same revision.
4. Precision of architecture, domain, command, and impact inferences after maintainer review.
5. Accepted, amended, rejected, disputed, and deferred baseline items.
6. Time for a new maintainer to explain current architecture and identify the next action.
7. Impact-analysis precision and missed affected surfaces found during review.
8. Context precision: necessary, irrelevant, and missing inputs to the implementation task.
9. First-review task acceptance, rework count, defects, and regression failures.
10. Full versus incremental ingestion time and the proportion of unchanged knowledge preserved.
11. Runtime/model changes completed without loss of task meaning.
12. Operational findings traced back to affected requirements, domain rules, and decisions.

Raw measurements, repository revision, analyzer versions, scope, reviewer rationale, and known benchmark limitations are retained. More extracted artifacts do not imply better understanding.

## Acceptance checklist for a completed journey

- Preflight made scope, exclusions, commands, risks, and proposed effects visible before ingestion.
- Default ingestion was local, read-only, offline, non-executing, and contained within the authorized root.
- Every observation was source-addressed; every inference exposed its basis, confidence, and alternatives.
- Unsupported and uninspected regions remained visible.
- An authorized maintainer itemized baseline acceptance and corrections.
- The waitlist request was evaluated against both accepted product knowledge and current repository evidence.
- Impact, design, work, task context, implementation, and evidence remained traceable.
- Hermes output and analyzer projections never became canonical truth automatically.
- Revision changes caused explicit staleness rather than mixed-state execution.
- Incremental re-ingestion preserved unaffected accepted knowledge and prior review history.
- Operational evidence could revise upstream knowledge only through proposal and approval.
- All benchmark observations were reproducible from referenced sources.

## Non-goals

This journey does not guarantee complete program comprehension, execute arbitrary repository code during ingestion, upload source by default, prescribe an analyzer implementation, require all Git history, reconstruct undocumented intent, mandate a particular waitlist design, or replace Git, CI, deployment, issue tracking, or telemetry systems. It does not create a separate brownfield domain model after convergence.

## Review decision

Reviewers should approve this journey when two independent implementations can safely inspect the same repository revision, expose comparable coverage and uncertainty, support itemized baseline approval, plan and verify the waitlist change, and preserve evolution history using the shared Echel contracts. Requested changes must identify an ambiguous safety, authority, decision, recovery, or measurement behavior rather than add speculative analyzer features.
