# Disposable SQLite/FTS index

`DisposableIndex` projects schema-valid canonical records into
`.echel/cache/index.sqlite3`. The database accelerates full-text lookup and
incoming/outgoing traversal of explicit relationships. It is a cache: deleting
it loses no product knowledge, and rebuilding it requires neither Hermes nor a
network connection.

`rebuild()` reads a deterministic canonical snapshot, creates a complete
temporary SQLite database, commits it, and atomically replaces the prior index.
It returns the index format, canonical fingerprint, record count, and explicit
relationship count. If validation or construction fails, the previous index is
left in place. Canonical files are never opened for writing.

`search(query, record_type=None, limit=20)` uses SQLite FTS5 and returns stable
record identity, type, revision, and canonical relative path. `related(id,
direction="both", predicate=None)` traverses only authored relationship records;
it never invents graph edges. Results are projections and cannot authorize or
revise knowledge.

Every query compares the stored source fingerprint with current canonical
bytes. A missing, stale, corrupt, or unsupported index fails with an actionable
`ECHEL-INDEX-*` error rather than returning incomplete results. Call `discard()`
and `rebuild()` to recover. Query input is parameterized, bounded to 100 results,
and invalid FTS syntax produces `ECHEL-INDEX-QUERY-INVALID`.

Index format `echel-index/v1` is internal and disposable, not a compatibility
promise. It may be replaced without a product-data migration as long as the
logical query behavior remains equivalent and canonical reconstruction remains
complete.
