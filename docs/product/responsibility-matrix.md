# Responsibility and authority contract

## Control

- Contract version: 1
- Product version: Echel 2
- Status: accepted
- Authority: Echel maintainers
- Last reviewed: 2026-07-15
- Depends on: [Echel 2 product contract](product-contract.md)
- Uses: [Echel 2 ubiquitous language](ubiquitous-language.md)
- Applies to: [Greenfield](greenfield-reference-journey.md) and [brownfield](brownfield-reference-journey.md) journeys

This contract assigns exactly one authoritative owner to each critical Echel 2 capability. Other participants may request, execute, mirror, cache, report, review, or approve work, but those activities do not transfer authority.

## Participants

| Participant | Meaning in this contract |
| --- | --- |
| **Authorized human** | A maintainer, product owner, reviewer, security authority, or operator acting within explicit project authority. Different decisions may require different humans. |
| **Echel** | The repository-native methodology and product-knowledge platform. |
| **Hermes** | The first runtime adapter target and owner of generic agent execution. Another conforming runtime can replace it. |
| **Git** | The repository revision system and its configured hosting service where applicable. |
| **CI** | The configured build and verification execution system. |
| **Deployment system** | The external system that changes and reports environment state. |
| **Telemetry system** | The external source authoritative for raw operational measurements, feedback, or incident signals. |
| **Configured artifact authority** | The single CI service or artifact registry selected by the project to own a given artifact identity. |
| **Executing tool** | The concrete local command runner or tool that owns the raw result of one local execution. |
| **Secret provider** | The concrete vault, operating-system facility, or external service selected to own secret values and access. |

An external system being authoritative for a raw result does not make it authoritative for Echel's interpretation of that result. An authorized human being accountable for a decision does not make manually maintained copies of system state authoritative.

## Authority rules

1. Every capability has one and only one authoritative owner.
2. Ownership means final authority over the named state or behavior, not responsibility for every action used to produce it.
3. Echel stores references and interpretations of external evidence; it does not duplicate external authority.
4. Hermes and other runtimes may propose knowledge changes but cannot accept them.
5. Humans approve consequential decisions; approval does not transfer technical system ownership to the approver.
6. Derived projections, indexes, caches, task context, chat history, and runtime memory never become authoritative through use or repetition.
7. A connector failure creates unavailable or stale evidence; it does not cause Echel to assume ownership of the external system.
8. If an integration cannot preserve these rules, Echel must deny the operation or expose it as unsupported rather than create split authority.

## Critical capability ownership

The `Capability` identifiers are stable references for architecture, protocol, policy, and task decisions. `Authoritative owner` must contain one participant. `Contributors and consumers` are deliberately non-authoritative.

| Capability | Authoritative owner | Authoritative state or decision | Contributors and consumers |
| --- | --- | --- | --- |
| CAP-METHOD | Echel | Lifecycle methodology, maturity reasoning, and next-action explanation | Authorized human reviews; Hermes may execute methodology tasks |
| CAP-KNOWLEDGE | Echel | Canonical product-knowledge records, provenance, relationships, and revisions | Humans and runtimes submit proposals; Git versions files |
| CAP-KNOWLEDGE-ACCEPT | Authorized human | Acceptance, rejection, amendment, or deferral of consequential product knowledge | Echel enforces policy and records the decision |
| CAP-FINDING | Echel | Finding, contradiction, staleness, and resolution workflow | Hermes, analyzers, CI, and humans report inputs |
| CAP-POLICY | Echel | Evaluation of project lifecycle, task, verification, and release policy | Humans own policy exceptions; external systems provide evidence |
| CAP-POLICY-EXCEPTION | Authorized human | Approval and expiry of a policy exception | Echel previews impact and records rationale |
| CAP-REPOSITORY-OBSERVE | Echel | Inspection scope, normalized observations, inferences, coverage, and approved baseline references | Files and Git provide evidence; analyzers produce proposals |
| CAP-REPOSITORY-REVISION | Git | Commits, trees, branches, tags, diffs, authorship, and repository revision identity | Echel and Hermes reference or request Git operations |
| CAP-MERGE | Authorized human | Whether a proposed code change is accepted into a protected integration branch | Git enforces repository rules; CI supplies checks |
| CAP-REQUIREMENT | Echel | Requirement records, relationships, revisions, and impact model | Human accepts intent; analyzers and runtimes propose findings |
| CAP-DOMAIN | Echel | Domain knowledge, terminology, rules, and explicit relationships | Domain reviewer authorizes consequential meaning |
| CAP-ARCHITECTURE | Echel | Architecture decisions, rationale, constraints, and impact relationships | Human accepts decisions; repository evidence informs them |
| CAP-PLAN | Echel | Roadmap outcomes, phases, work items, dependencies, priority model, and staleness | Humans set priorities; external trackers may mirror state |
| CAP-TASK | Echel | Immutable task specification identity, semantics, acceptance conditions, and source revisions | Humans authorize execution; runtimes consume it |
| CAP-CONTEXT | Echel | Context selection, ranking, budget, protected content, and inclusion explanation | Runtime reports model limits; sources retain original authority |
| CAP-RUNTIME-PROTOCOL | Echel | Versioned runtime-neutral request, event, result, and error semantics | Hermes adapter implements; alternative runtimes conform |
| CAP-MODEL | Hermes | Model/provider discovery, selection, invocation, failover, and model usage accounting | Echel supplies constraints and receives normalized usage |
| CAP-SESSION | Hermes | Agent session, context-window use, runtime memory, prompts, delegation, and internal execution loop | Echel supplies task/context/policy; human may cancel |
| CAP-TOOLS | Hermes | Tool discovery, invocation mechanics, streaming, and runtime-level tool errors | Echel bounds allowed capabilities; tools own their external effects |
| CAP-EXECUTION-POLICY | Echel | Allowed capability set, workspace boundary, budgets, approvals required, and task execution constraints | Human authorizes exceptions; Hermes enforces mapped permissions |
| CAP-RUN | Echel | Durable run identity, attempts, lifecycle, normalized events/results, and relation to task/revision | Hermes owns active session; Git/CI provide references |
| CAP-WORKSPACE | Git | Worktree/branch revision state and commit objects | Echel requests isolation; Hermes operates only within granted path |
| CAP-BUILD | CI | Authoritative CI job execution, logs, status, timing, and artifacts | Git triggers; Echel imports references and evaluates evidence |
| CAP-LOCAL-CHECK | Executing tool | Raw local command execution, exit status, stdout, and stderr | Hermes invokes under Echel policy; Echel records normalized evidence |
| CAP-VERIFICATION | Echel | Mapping acceptance conditions to evidence and verification decision state | CI/tools supply raw results; reviewer approves where policy requires |
| CAP-REVIEW | Authorized human | Independent review acceptance, rejection, or requested change | Echel assembles evidence and records decision; CI supplies checks |
| CAP-RELEASE-KNOWLEDGE | Echel | Release intent, included work, verification relationships, risks, and approval record | Git/CI/registry provide revision and artifact evidence |
| CAP-RELEASE-APPROVAL | Authorized human | Authorization to publish or deploy a release | Echel evaluates policy; external systems enforce credentials |
| CAP-ARTIFACT | Configured artifact authority | Built artifact bytes, digest, signature, storage, and availability | Echel references identity and evidence; human authorizes promotion |
| CAP-DEPLOY | Deployment system | Deployment execution, target-state change, raw status, and rollback execution | Echel generates specification; authorized human approves |
| CAP-SECRET | Secret provider | Secret value, access control, rotation, and audit at source | Echel stores only safe references; Hermes receives scoped access when authorized |
| CAP-TELEMETRY | Telemetry system | Raw metrics, logs, traces, feedback, and incident source events | Echel imports references and proposes operational findings |
| CAP-LEARNING | Echel | Operational finding interpretation, impact propagation, and knowledge proposals | Human approves upstream revisions; telemetry supplies evidence |
| CAP-EXTENSION | Echel | Extension contracts, compatibility rules, isolation policy, and registration state | Extension authors implement; runtime executes runtime-owned skills |

`Executing tool`, `configured artifact authority`, and `secret provider` are role labels for the concrete external system selected by a project. A project configuration must bind each used role to one system before execution, never multiple systems for the same identity.

## Decision accountability

System ownership and human accountability are separate:

| Decision | Accountable authority | Required input | Recorded by |
| --- | --- | --- | --- |
| Accept product intent, domain meaning, or architecture | Authorized product/domain/architecture human | Provenance, alternatives, uncertainty, and impact | Echel |
| Permit risky tools, network, secrets, or expanded workspace | Authorized security or repository human | Exact capability preview, scope, duration, and risk | Echel; enforced by Hermes/external system |
| Accept code into protected history | Authorized repository reviewer | Diff, task intent, review, and required CI evidence | Git; referenced by Echel |
| Approve a release or deployment | Authorized release/operator human | Policy assessment, immutable revision/artifact, risks, and rollback | Echel plus external approval record |
| Accept operational learning into upstream knowledge | Authorized product/technical human | Source telemetry, interpretation, confidence, and impact | Echel |

No agent, model, analyzer, CI result, score, or policy engine can impersonate these authorities. Projects may pre-authorize low-risk decisions through explicit policy, but the policy and its scope remain human-approved and auditable.

## Boundary interaction contracts

### Echel to runtime

Echel sends an immutable task specification, explainable context bundle, versioned runtime protocol, capability allowlist, workspace reference, budgets, cancellation channel, and expected result schema. It never sends product secrets as ordinary context.

Hermes returns capability discovery, normalized events, terminal state, usage, external-effect references, patches or commit references, evidence, findings, and knowledge proposals. Runtime-specific prompts, model APIs, session memory, and delegation trees remain inside Hermes unless exposed as optional diagnostic evidence.

Echel may reject dispatch before side effects when the task or context revision is stale, capabilities are unavailable, policy denies execution, required approval is absent, or protocol versions are incompatible. Hermes must reject permissions it cannot enforce rather than silently broaden them.

### Echel to Git

Echel reads revision identity and history and may request isolated branches/worktrees or commits through an adapter. Git remains authoritative for file and revision state. Echel records stable references and detects staleness; it does not maintain a competing commit graph or decide protected-branch merge policy.

### Echel to CI

Echel submits or discovers verification requests and imports immutable job, check, log, and artifact references. CI owns execution and raw status. Echel owns whether those results satisfy a task acceptance condition or release policy. A green CI check is evidence, not automatic product acceptance.

### Echel to deployment and telemetry

Echel produces a deployment specification and records approval and intended revision/artifact. The deployment system owns execution and environment state. Telemetry systems own raw operational signals. Echel relates returned evidence to releases and opens findings; it does not silently reinterpret an external status as product success.

### External trackers and rendered documentation

Issue trackers, project boards, documentation sites, and dashboards are mirrors or projections unless a future contract explicitly assigns a bounded external authority. Synchronization conflicts resolve in favor of canonical Echel records for product knowledge and planning, and in favor of the external owner for its raw system state.

## End-to-end execution sequence

```text
authorized human accepts intent in Echel
  → Echel creates work and immutable task/context contracts
  → authorized human grants required execution capability
  → Git supplies an isolated revision/workspace
  → Echel dispatches through the runtime protocol
  → Hermes owns model, session, tools, and delegation
  → Git owns resulting code revisions
  → CI owns raw verification execution
  → Echel evaluates evidence against intent and policy
  → authorized humans review, merge, release, or deploy
  → deployment/telemetry systems own raw outcomes
  → Echel proposes learning; authorized humans accept revisions
```

This sequence applies to both reference journeys. Greenfield and brownfield differ before accepted intent and baseline exist, not at the task/runtime/evidence boundary.

## Denial, interruption, and conflict handling

| Condition | Required behavior | Authority preserved |
| --- | --- | --- |
| Hermes lacks a requested capability | Echel does not dispatch and reports the missing capability or alternative | Hermes owns actual runtime capability; Echel owns task policy |
| Hermes requests broader tool access | Echel denies it until an authorized human approves a revised policy | Human owns exception; Echel records; Hermes enforces |
| Task or repository revision is stale | Echel invalidates preparation and requires impact/context recompilation | Echel owns task validity; Git owns current revision |
| Runtime is interrupted after external effects | Hermes returns known events; Echel records an incomplete attempt and reconciles stable external references | Each external system retains its state; no synthetic success |
| Local result and CI result disagree | Preserve both; use policy to determine required authority and open a finding | Each executor owns its raw result; Echel owns evaluation |
| Echel record and Git disagree about a commit | Git wins on commit existence/content; Echel marks its reference stale or invalid | No duplicate revision authority |
| Echel projection and canonical record disagree | Canonical record wins and projection is rebuilt | Echel canonical store remains sole product truth |
| External tracker and Echel plan disagree | Echel plan wins for methodology/planning; synchronization reports conflict | Tracker remains authoritative only for its native metadata |
| Deployment reports failure despite release approval | Deployment outcome remains failed; Echel opens a finding and preserves approval history | Approval is not rewritten; external outcome is not overridden |
| Telemetry interpretation is disputed | Raw telemetry reference remains; Echel records competing inference and review state | Telemetry owns measurement; human accepts interpretation |
| Owner is unavailable | Operation pauses or follows an explicit delegated authority policy | Authority is never inferred from tool availability |

Retry, resume, fallback, and reconciliation create explicit attempts or decisions. They never overwrite prior evidence or transfer ownership to the component that recovered the workflow.

## Extension rule

A new integration or capability must declare:

1. its stable capability identifier;
2. exactly one authoritative owner;
3. authoritative state and non-authoritative copies;
4. allowed producers, consumers, and mutations;
5. approval and least-privilege requirements;
6. version, idempotency, cancellation, error, and reconciliation semantics;
7. behavior when its owner is unavailable; and
8. migration from any capability it supersedes.

Review rejects a proposal with no owner, multiple owners, implicit authority transfer, or an unresolvable conflict with this contract.

## Non-goals

This matrix does not prescribe vendor products, Git hosting, CI configuration, deployment topology, model selection, UI, internal Hermes design, organization chart, or a universal RACI process. It does not make Echel an orchestrator for systems it only references, and it does not make humans the storage authority for machine-owned state.

## Review decision

Reviewers should approve this contract when every critical capability has one authoritative owner; both reference journeys can cross each boundary without split ownership; denial, interruption, stale state, and conflicting evidence preserve authority; and a future adapter can determine exactly which state it may read, propose, mutate, or only reference.
