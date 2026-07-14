# Contribution and task-packet workflow

## Control

- Workflow version: 1
- Product version: Echel 2
- Status: proposed for contributor-workflow review
- Authority: Echel maintainers
- Last reviewed: 2026-07-15
- Template: [task-packet-template.md](task-packet-template.md)

This workflow gives human and AI-assisted contributors one consistent path from selecting work to an attributable review decision. A task packet is a planning and handoff contract. It is not the future runtime `task specification`, which Echel will compile immutably from accepted work at a known revision.

## Roles and authority

| Role | Responsibility | Cannot do implicitly |
| --- | --- | --- |
| Maintainer/triager | Approves task readiness, priority, dependencies, owner, and reviewer | Treat an idea or issue title as implementation-ready |
| Owner/contributor | Implements one claimed task, verifies it, and reports findings | Expand scope, accept own consequential knowledge, or change external state beyond granted permissions |
| Reviewer | Independently checks intent, behavior, evidence, risks, and maintainability | Replace failed evidence with trust in the contributor or model |
| Product/domain/security authority | Decides consequential meaning, exceptions, and bounded permissions | Delegate authority merely by making a tool available |
| Runtime/agent | Executes within the packet’s Hermes contract and returns normalized outputs | Approve its own result, task mutation, or knowledge proposal |

One person may hold multiple roles in a small project, but each decision and its basis remain explicit. Self-review does not satisfy an independent-review requirement.

## Workflow states

```text
proposed → planned → ready → in progress → review → done
                 ↘ blocked ↗       ↘ changes requested ↗
```

| State | Entry rule | Exit rule |
| --- | --- | --- |
| Proposed | A problem or outcome is submitted with provenance | Maintainer rejects, defers, merges, or creates a complete packet |
| Planned | Packet is complete but dependencies, milestone, authority, or capacity are not clear | All readiness checks pass |
| Ready | Dependencies are done, owner/reviewer can be assigned, and no unresolved gate prevents work | Owner claims against a specific repository revision |
| In progress | One owner and start revision are recorded | Verified handoff enters Review, or a concrete impediment enters Blocked |
| Review | Patch/commit, acceptance mapping, and required evidence are available | Reviewer accepts to Done or returns exact changes |
| Changes requested | Review identifies unmet conditions without changing the task’s objective | Owner addresses findings and returns to Review; changed objective requires replanning |
| Blocked | A named external dependency, authority, permission, or decision prevents meaningful progress | Evidence shows the impediment is resolved, then return to Planned/Ready/In progress as appropriate |
| Done | Authorized review accepts the outcome and required knowledge/status updates | Immutable history; later defects create findings/new work rather than rewriting completion |

`ready` may be calculated by a board; every other state transition is an attributable decision. WIP limits are project policy. A contributor must not start another task merely because a slot exists when their current work can be completed or reviewed.

## 1. Propose or select

A selectable task has:

- a stable ID and observable objective;
- rationale tied to product intent, evidence, an ADR, or an upstream task;
- explicit scope and non-goals;
- dependencies and current repository/knowledge revisions;
- testable acceptance conditions;
- exact verification expectations;
- risk, rollback, compatibility, security, and knowledge-update implications;
- an execution contract describing context, tools, permissions, budgets, and expected outputs;
- an owner and independent reviewer before implementation begins.

Selection procedure:

1. Refresh the project’s authoritative task view.
2. Finish or hand off current in-progress work.
3. Consider only Ready tasks whose dependencies are accepted and whose external conditions are satisfied.
4. Rank by project priority, milestone/dependency unlock value, then stable task ID; maintainers may override with recorded rationale.
5. Read the entire packet and its direct dependency outputs.
6. Verify that the working tree and start revision are understood.
7. Claim the task atomically; if another owner already claimed it, stop and select again.

A one-line title, chat request, generated plan, or unreviewed issue is not a valid task packet.

## 2. Prepare and preview

Before mutation, the owner records or confirms:

- repository start revision and relevant canonical-record revisions;
- files/components and public contracts likely affected;
- task-specific verification and full baseline commands;
- required tools, filesystem/network/Git permissions, and forbidden operations;
- fixture versions, secrets/data policy, budgets, cancellation, and delegation limits;
- compatibility/migration expectations and safe rollback;
- known dirty-worktree changes and how they will be preserved.

Any proposed external effect, destructive action, secret access, network use, release/deployment, or authority change is previewed and approved by the correct human before execution. Approval is scoped to the stated effect; it does not authorize adjacent work.

If the task contradicts an accepted contract or ADR, stop and create a finding/proposal. Do not implement the contradiction and edit the documentation afterward to match.

## 3. Execute

1. Move the task to In progress and record owner/start revision.
2. Reproduce the relevant baseline before changing code when feasible.
3. Implement the smallest vertical outcome within scope.
4. Test close to the change while working.
5. Preserve deterministic output, provenance, stable identifiers, and structured errors for public machine interfaces.
6. Keep optional/runtime/external behavior behind its owning boundary.
7. Record new contradictions, missing requirements, or adjacent opportunities as findings; do not silently add features.
8. If upstream state changes, stop, assess impact, and revalidate or replan rather than continuing against stale context.

An AI agent receives only the packet, direct dependencies, affected canonical records/ADRs, relevant code/tests, and an explicit context budget. Delegation is bounded and child work cannot broaden permissions or authority. Runtime transcripts remain diagnostic; durable discoveries return as findings or proposals.

## 4. Verify

Verification is layered:

1. Focused tests for the changed behavior and highest-risk failures.
2. Contract/schema/fixture compatibility checks where applicable.
3. Security, migration, recovery, performance, or usability checks required by the packet.
4. Full repository baseline: `make verify`.
5. Patch hygiene: `git diff --check`, status review, and staged-diff inspection before commit.

For each acceptance condition, handoff names the evidence that supports it. Not applicable checks require rationale. A failure is retained and either corrected, returned as an open finding, or used to block review. Tests may not be weakened, skipped, or rewritten merely to accept existing incorrect behavior.

## 5. Handoff and review

The owner submits:

- task ID, objective, start/end revisions, and patch/commit;
- concise implementation summary and affected contracts;
- acceptance-condition-to-evidence mapping;
- exact commands and outcomes, including failures/retries;
- compatibility, migration, security, performance, and rollback assessment;
- external effects and approvals used;
- findings, proposed knowledge changes, and accepted exceptions;
- explicit reviewer decisions required and recommended next task.

The reviewer independently:

1. checks that the objective—not just the activity list—is satisfied;
2. reads affected governing contracts and the diff;
3. reproduces risk-proportional verification;
4. challenges scope, duplication, authority drift, weak abstractions, and unnecessary complexity;
5. confirms failures/recovery and compatibility where relevant;
6. verifies findings/proposals were not silently accepted;
7. records `accept`, `changes requested`, or `reject` with exact evidence.

Acceptance moves the task to Done only after required documentation, task dependencies, board state, and knowledge proposals are resolved. A merge is not automatically a task acceptance, and task acceptance is not automatically a release approval.

## 6. Commit and integration

Use a focused commit whose message describes the outcome. Stage only task files and reviewed supporting updates. Do not include private workspace files, unrelated user changes, generated caches, secrets, or evaluator-only benchmark oracles.

Before commit:

```bash
git diff --check
git status --short
git diff --cached
```

The pull request or patch is linked to the task. Protected-branch merge follows repository review and CI policy. Push, merge, release, deployment, issue closure, and external messages occur only when requested or explicitly part of the accepted workflow.

## Interruption, denial, and recovery

| Condition | Required response |
| --- | --- |
| Dependency or source revision changed | Mark work stale, preserve the patch, reassess impact, and rebase/recompile only after review |
| Task objective becomes ambiguous | Stop mutation, record the exact ambiguity, and return to Planned or Changes requested |
| Another contributor claims the task | Do not race; retain analysis as a handoff and select other work |
| Required permission is denied | Preserve safe progress, report the minimum permission or alternative, and never bypass the denial |
| Tool/runtime is interrupted | Record attempt and external effects, reconcile stable references, then resume/retry as an explicit attempt |
| Verification fails | Keep task out of Review unless the failure is an accepted, documented exception with authority and expiry |
| Reviewer finds out-of-scope work | Split or remove it; do not enlarge acceptance after implementation |
| Commit contains unrelated or sensitive data | Stop integration, remove it safely while preserving user work, and re-verify |
| Contributor becomes unavailable | Record current revision, status, evidence, unknown effects, and next action before reassignment |
| Board or external tracker disagrees | Resolve according to the authoritative project task record; report synchronization conflict |

Rollback restores the last valid project/code revision without deleting evidence or accepted history. A rolled-back implementation remains a recorded attempt and may create a finding or corrective task.

## Task-packet change control

- Before In progress, maintainers may revise a packet while retaining change history.
- After In progress, acceptance conditions may be clarified but not weakened or materially expanded without returning to Planned and recording the decision.
- An immutable runtime task specification is never edited; changed work compiles a new specification with lineage.
- Dependency completion does not validate semantic compatibility automatically; the owner verifies consumed contracts.
- Duplicate tasks are merged under one ID with redirects/relationships so they do not become two sources of work truth.
- Cancellation records reason, authority, partial effects, and disposition of findings/evidence.

## Public board and private planning

The public workflow is tool-neutral. A project may use repository records, GitHub/GitLab issues, or another tracker as a view, but must declare which task representation is authoritative and how conflicts are resolved.

Echel’s internal `echelit/` directory is ignored and remains a private implementation workspace. Its Kanban helps maintainers execute the Echel 2 roadmap, but public contributors must not depend on files unavailable in the repository. Before community contribution begins, maintainers publish or copy the relevant accepted task packet into the chosen public collaboration system.

## Workflow acceptance

This workflow is acceptable when a contributor unfamiliar with the private planning workspace can select a complete ready task, determine permitted work, implement it without reconstructing hidden intent, reproduce required verification, hand off evidence, and receive an attributable review decision without granting an agent or external tracker canonical authority.
