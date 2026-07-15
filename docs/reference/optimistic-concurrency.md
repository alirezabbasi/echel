# Record revisions and optimistic concurrency

Every canonical record begins at revision 1 and advances by exactly one for each
semantic update. Before writing, a caller supplies a `RecordExpectation`:

- `RecordExpectation.absent()` explicitly creates a record that was not observed;
- `RecordExpectation.at_revision(n, digest)` updates the exact state observed.

`CanonicalRecordStore.observe(record)` returns the current revision and SHA-256
digest. The digest detects direct edits that failed to advance the record's
revision. The write boundary validates the expectation again while holding the
repository write lock, so the state check and atomic replacement cannot race
another conforming Echel writer.

An unexpected current revision, digest, existence, or absence raises
`RecordConflictError` (`ECHEL-RECORD-CONFLICT`). The error reports expected and
actual state and tells the caller to reload, merge, and retry; it never overwrites
the winner. New records must use revision 1 and updates must use the current
revision plus one. Identical retries are safe no-ops even if their original
precondition is now stale.

The lock is operational coordination, not canonical knowledge. If a process is
known to have terminated while leaving `.echel/write.lock`, an operator may remove
that stale file after confirming no Echel writer is active. Echel does not break
locks automatically because doing so could destroy a live writer's exclusion.

Transactions capture these preconditions during preparation and persist them in
the journal. Recovery reuses the original expectations; records already applied
before interruption are identical no-ops, while unrelated intervening changes
produce a semantic conflict and halt recovery for review.
