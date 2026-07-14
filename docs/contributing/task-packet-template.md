# E2-NNN — Task title

## Control

- Status: proposed
- Priority: P0/P1/P2
- Milestone: M#
- Initiative: I##
- Owner: unassigned
- Reviewer: unassigned
- Dependencies: task IDs or `none`
- Start revision: unset
- Knowledge revisions: unset

## Objective

One observable outcome. Describe what a user, contributor, or system can demonstrate when the task is complete.

## Rationale and source

Identify the product promise, reference journey, evidence, accepted decision, finding, or upstream task that requires this work. Link exact revisions.

## Scope

- Exact behaviors, contracts, and components included.
- Expected public interfaces and files when known.

## Out of scope

- Adjacent behavior intentionally deferred.
- Compatibility or migration deliberately not promised, with rationale.

## Inputs and constraints

- Direct dependency outputs and revisions.
- Governing product contracts and ADRs.
- Data, security, authority, compatibility, portability, accessibility, and performance constraints.
- Dirty-worktree or external-state assumptions.

## Implementation approach

Small ordered steps. Prefer one vertical outcome. Stop and propose an ADR before changing a foundational boundary.

## Acceptance criteria

- [ ] Observable objective is demonstrated.
- [ ] Relevant domain, schema, protocol, and authority invariants pass.
- [ ] Invalid input, denial, interruption, stale state, and recovery behavior pass where applicable.
- [ ] Compatibility, migration, security, performance, and usability expectations pass where applicable.
- [ ] Documentation and knowledge implications are resolved.
- [ ] Full repository verification passes without weakening policy or tests.

## Verification

- Focused command and expected evidence.
- Integration/scenario/fixture command and version.
- `make verify`.
- `git diff --check` and staged-diff review.
- Manual, security, performance, migration, recovery, or usability review where required.

Map every acceptance criterion to an evidence location or explain why it is not applicable.

## Hermes execution contract

- Recommended runtime/model/skill capabilities.
- Required tools and explicit forbidden operations.
- Filesystem, network, shell, Git, secret, and external-system permissions.
- Workspace and start revision.
- Allowed context sources, protected content, and token/cost/time budgets.
- Cancellation, retry, delegation, iteration, and concurrency limits.
- Required normalized outputs, evidence, findings, and separate knowledge proposals.

## Risks and rollback

- Risks and mitigations introduced by the task.
- Last valid state and rollback/forward-recovery steps.
- Treatment of partial external effects, schemas, migrations, and user data.

## Knowledge updates

- Canonical records, ADRs, public documentation, task dependencies, metrics, and roadmap assumptions that may change.
- Findings/proposals that require separate authority.

## Evidence and handoff

- Start/end repository revision and focused commit/patch.
- Acceptance-to-evidence mapping and exact verification results.
- Compatibility, security, migration, performance, usability, and recovery evidence.
- External effects and approvals.
- Open findings, rejected scope, and accepted exceptions with authority/expiry.
- Reviewer decision and remaining actions.
- Downstream tasks unblocked/invalidated and recommended next task.
