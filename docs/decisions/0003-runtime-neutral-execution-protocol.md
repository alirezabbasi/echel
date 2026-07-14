# ADR-0003: Runtime-neutral execution protocol

- Status: Accepted
- Date: 2026-07-15
- Decision owners: Echel maintainers
- Depends on: responsibility and authority contract v1
- Supersedes: direct coupling between Echel methodology and agent/runtime internals

## Context

Echel must prepare implementation-ready work that can survive model and runtime changes. Hermes is the first runtime companion and provides multi-model execution, tools, skills, session memory, and delegation. If Echel imports Hermes internals, embeds provider prompts, or stores Hermes session state as product truth, task meaning and project memory become runtime-dependent.

## Decision

Echel integrates with Hermes and future agent systems through a narrow, versioned, runtime-neutral protocol owned by Echel.

- Echel owns immutable task semantics, context selection, execution policy, durable run identity, expected event/result shapes, acceptance mapping, and normalized findings/proposals.
- A runtime owns capability discovery, model/provider calls, prompts, context-window management, runtime memory, agent loop, tool mechanics, and bounded delegation.
- Dispatch carries protocol version, immutable task and context revisions/digests, workspace reference, capability allowlist, budgets, approvals, cancellation contract, idempotency key, and expected outputs.
- Results distinguish terminal state, attempts, events, usage, tool effects, patch/commit references, evidence, findings, and knowledge proposals. Runtime output cannot accept its own knowledge or work.
- Capability discovery precedes dispatch. Unsupported protocol versions, unenforceable policy, stale revisions, or missing required capabilities fail before side effects.
- Hermes-specific translation lives in an adapter. Domain and application services never import Hermes packages or provider SDKs.
- The protocol supports local process transport first. Transport can change independently from message semantics.

E2-065 defines exact schemas and compatibility fixtures. This ADR fixes ownership and semantic boundaries, not wire encoding or Hermes implementation details.

## Consequences

Benefits:

- task meaning survives runtime/model replacement;
- Echel remains testable with a deterministic fake runtime;
- Hermes can evolve its agent loop without migrating product knowledge;
- security and authority decisions are explicit before execution.

Costs:

- adapter and protocol-version maintenance;
- some runtime-specific capabilities require negotiated extensions or remain unavailable;
- normalized events may omit provider-specific diagnostic detail;
- cancellation, retry, and partial external effects need careful reconciliation.

## Failure and recovery

- Dispatch is idempotent by task/run attempt key; retry never implies duplicate authorization.
- Cancellation propagates, but Echel records that external effects may outlive a lost runtime response and reconciles stable Git/tool references.
- Runtime unavailability leaves planning, task compilation, context inspection, and verification imports usable.
- Unknown result fields are preserved where safe but do not change semantics; unknown required protocol features reject compatibility.
- Runtime memory loss creates a new or resumed attempt according to declared capability, never reconstructed product truth.
- Findings and proposals are staged separately from code/evidence and require Echel policy and human authority.

## Alternatives considered

- **Make Hermes Echel’s internal execution module:** fastest initially but couples product knowledge and roadmap to one runtime. Rejected.
- **Shell out with an unversioned prompt:** simple but cannot express capability, policy, events, cancellation, or stable results. Rejected.
- **Adopt one provider API as the protocol:** broad tooling but makes provider semantics authoritative. Rejected.
- **Let every adapter define its own task schema:** flexible but destroys portability and comparability. Rejected.
- **Build a second agent loop in Echel:** duplicates Hermes and violates product scope. Rejected.

## Replacement conditions

The protocol may gain compatible versions through its normal evolution rules. Moving model/tool/session ownership into Echel, allowing runtime memory to become canonical product knowledge, or adopting a runtime-owned task meaning requires a superseding ADR and product-contract revision.
