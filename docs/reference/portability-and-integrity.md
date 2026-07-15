# Portability and integrity diagnostics

`PortableRepositoryService.export()` creates deterministic `echel-export/v1`
JSON bytes containing every schema-valid canonical record, its canonical path,
and a bundle fingerprint. It preserves record revisions, authority, and
provenance. Cache databases, transaction or migration journals, backups, runtime
memory, Git metadata, and generated views are intentionally excluded.

`preview_import(content, transaction_id)` is non-mutating. It checks the format,
100 MiB size bound, fingerprint, schema versions, schemas, identifiers, canonical
paths, deterministic ordering, duplicate identities, and relationship endpoints.
Import targets must be initialized and empty; merge semantics belong to explicit
record workflows and are never guessed. `apply_import(plan)` rechecks the target
and plan fingerprint, then uses the durable multi-record transaction journal for
all-or-nothing installation. Empty bundles are a safe no-op.

`IntegrityService.inspect()` reads raw canonical files without repairing them.
It reports corruption, unsupported schema versions, schema or identity failures,
duplicate identities, orphan relationship endpoints, and missing, stale,
corrupt, or unsupported disposable indexes. Every issue has a stable
`ECHEL-INTEGRITY-*` code, severity, path, explanation, and remedy. A missing
optional index is a warning and does not make canonical state unhealthy.

Diagnostics never edit records, delete links, migrate versions, or rebuild the
index automatically. Typical remedies are restoring reviewed bytes from Git or
a verified backup, running an explicit migration, reconciling an orphan through
a canonical change, or discarding and rebuilding the disposable index. This
keeps recovery visible and reviewable instead of allowing convenience tooling to
become an authority boundary.
