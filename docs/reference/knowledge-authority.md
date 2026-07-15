# Knowledge proposals and authority

Claims, decisions, and operational learnings are protected knowledge. Agents,
analyzers, imports, and systems may create `proposed` records, but cannot promote
them to `accepted` or `rejected`. Those decisions require a human principal with
the explicit `knowledge:decide` capability.

`KnowledgeAuthorityService.preview(...)` loads the current proposal, validates
the principal, action, rationale, and timestamp, and returns an explainable
non-mutating transition. `apply(...)` revalidates the transition and writes it
through optimistic concurrency. A parallel decision therefore wins once; stale
reviewers receive a semantic conflict and cannot overwrite it.

The decided record advances exactly one revision and keeps its original proposal
provenance. Its `authority` evidence records:

- accepted or rejected action;
- authorized human identity and capability;
- decision rationale and timestamp;
- exact proposal revision reviewed.

The v1 schema requires this evidence for accepted or rejected protected records
and requires its action to match status. Rejection preserves the proposal and its
history; it is not deletion. Superseding accepted knowledge, resolving findings,
policy exceptions, releases, deployments, and delegated low-risk policy require
their own lifecycle contracts and are not silently generalized here.

The service trusts an upstream identity adapter to authenticate the principal;
declaring an arbitrary string as a user is not authentication. Hermes remains
behind `AgentRuntime` and receives no authority token through this service.
