# Query, reverse-link, and impact APIs

`QueryService` is the read-only application boundary for finding and explaining
canonical product knowledge. SQLite accelerates candidate selection and
traversal, but every returned item is reloaded from `CanonicalRecordStore` and
includes its canonical provenance, revision, and relative path. The service
rechecks index freshness before returning.

`search(query, record_type=None, limit=20)` returns complete provenanced records,
not index-owned excerpts. `reverse_links(record_id, predicate=None)` returns
incoming authored relationships with their reason, direction, provenance, and
the provenanced source record.

`impact(record_id, max_depth=3)` performs a bounded breadth-first traversal and
returns one deterministic shortest path per affected record. Each step names the
relationship, predicate, stated reason, traversal direction, and relationship
provenance. Cycles never repeat a record. The `explicit-impact/v1` direction
policy is intentionally small:

- `informs`, `supports`, `contradicts`, and `affects` propagate source to target;
- `depends_on`, `implements`, and `verifies` propagate target to source.

This is an impact-candidate query, not proof that a change is required. It adds
no inferred relationship and makes no knowledge decision. Missing records,
invalid identifiers or bounds, stale projections, and repository mismatches
fail with structured `ECHEL-QUERY-*` or `ECHEL-INDEX-*` errors.

Adding a predicate or changing its impact direction changes the logical policy
and requires explicit review. Alternative path enumeration, weighted traversal,
code-symbol impact, and probabilistic inference remain outside this initial API.
