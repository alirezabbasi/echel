# ADR-0002: Disposable projections and indexes

- Status: Accepted
- Date: 2026-07-15
- Decision owners: Echel maintainers
- Depends on: ADR-0001
- Supersedes: canonical product/knowledge graph and duplicated v1 reports

## Context

Users and tools need search, reverse links, impact traversal, documentation, status summaries, dashboards, and exports. Computing every view by scanning records may become slow, but storing each view as authority recreates duplicated truth and synchronization debt.

## Decision

All query indexes, search databases, relationship graphs, rendered documentation, status reports, dashboards, and external tracker mirrors are disposable projections of canonical records and referenced external authority.

- Canonical records store only explicit, typed, justified relationships. A graph view is not a second relationship store.
- A local SQLite/FTS database is the preferred initial search and traversal index, subject to E2-023 evidence. It is never required for canonical recovery.
- Every projection declares generator identity/version, source project revision or record-revision set, generation time, and output schema/version.
- Echel detects missing, stale, incompatible, corrupt, or partial projections and rebuilds them deterministically or reports why it cannot.
- Projection generation is read-only with respect to canonical knowledge. Discoveries become findings or proposals through the application boundary.
- Generated outputs live outside canonical record collections and are ignored by Git by default unless a project intentionally publishes a deterministic snapshot.
- External trackers and documentation systems remain mirrors for Echel-owned knowledge; synchronization conflicts are explicit.

## Consequences

Benefits:

- no synchronization between competing canonical representations;
- indexes and renderers can evolve or be replaced independently;
- fast query does not compromise reviewable storage;
- corruption recovery is rebuild rather than manual truth reconciliation.

Costs:

- first query or rebuild can be slower;
- stale detection and generator compatibility require disciplined metadata;
- published projections can confuse users unless clearly labeled;
- external edits to mirrors require a proposal/import path rather than direct acceptance.

## Failure and recovery

- Index absence never prevents canonical validation, mutation, export, or migration.
- Interrupted generation writes to a temporary generation and atomically promotes only a complete result.
- A source revision mismatch makes a projection stale; Echel never presents it as current without a warning.
- Rebuild output for identical sources and generator version must be semantically deterministic.
- If an external mirror changes independently, Echel previews a conflict and proposed import; it does not overwrite either side silently.

## Alternatives considered

- **Canonical graph database:** flexible traversal but duplicates record authority and raises deployment complexity. Rejected.
- **Persist every generated document in Git:** reviewable but creates noisy diffs and stale copies. Optional only for intentional publication.
- **No indexes:** simplest initially but inadequate for impact and context benchmarks at scale. Rejected as a permanent constraint.
- **Update projections transactionally with records:** appears consistent but couples every mutation to optional consumers and expands failure scope. Rejected.

## Replacement conditions

Individual index or projection technologies may change without an ADR when the logical contract remains intact. Making any derived view authoritative, non-rebuildable, or required to recover product truth requires a superseding ADR and migration design.
