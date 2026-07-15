# Explicit relationships

Relationships are sparse canonical records that connect two existing records for
one stated reason. They are not inferred graph edges, backlinks, or a cache.
Indexes and graph views may project them, but the relationship record remains the
only authoritative link.

`RelationshipService.preview(...)` requires a stable relationship identifier,
existing typed source and target identifiers, a predicate, a non-empty reason,
provenance, and a timestamp. It validates the link against the active versioned
policy and returns a non-mutating explanation. `apply(...)` rechecks endpoints
and policy before atomically creating revision one with an absent-record
precondition.

The built-in `core/v1` policy intentionally contains a small vocabulary:
`informs`, `supports`, `contradicts`, `depends_on`, `implements`, `verifies`, and
`affects`. Each predicate permits only meaningful source/target record families.
Unknown predicates, invalid directions, self-links, missing endpoints, and links
without rationale are denied with `ECHEL-RELATIONSHIP-*` errors. A new semantic
need should justify a reviewed policy revision, not use a vague catch-all edge.

Every relationship also carries the ordinary canonical provenance envelope.
`reason` explains this particular connection; provenance identifies who or what
proposed it; `policy` records the contract that allowed it. These fields have
different purposes and none may be inferred from another.

The schema change is intentionally strict: older relationship records without
`reason` and `policy` no longer satisfy schema version 1 and must be enriched
before being written. E2-022 will provide general migration mechanics. Rolling
back this capability means restoring the earlier schema and service code; it
must not silently discard relationship records already created under `core/v1`.
