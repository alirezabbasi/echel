# Schema migrations

Canonical record readers never guess how to interpret unsupported schemas.
`MigrationService.preview(...)` is the separate compatibility boundary for a
repository-wide upgrade. It reads raw canonical bytes, requires one source
version across the repository, applies a registered migration path, validates
every target against the current schema, and returns record IDs, paths, versions,
backup location, and journal location without mutation.

Migration from pre-public schema version `0` to version `1` requires explicit
per-record resolutions for meaning that cannot be inferred safely. A resolution
may remove named legacy fields or set reviewed target fields. For example, the
caller must select a missing project profile and supply missing claim kind/stage;
Echel does not invent them. Every migrated record advances its record revision,
updates its timestamp, preserves existing provenance, and records namespaced
migration metadata.

Applying a plan follows a recoverable protocol:

1. Recheck every source digest captured by preview.
2. Persist an exact byte-for-byte backup and manifest under
   `.echel/backups/<id>/`.
3. Persist validated target bytes and `prepared` intent under
   `.echel/migrations/<id>/`.
4. Durably select `committing`, then replace each canonical file atomically.
5. Remove the completed journal while retaining the backup.

Recovery deletes a merely prepared journal because no canonical mutation began.
It rolls a committing journal forward, accepting already-installed target bytes
as idempotent progress. Source drift, corrupt staged content, path escape,
unknown versions, unsupported targets, and mixed-version repositories stop with
stable `ECHEL-MIGRATION-*` errors.

Rollback restores exact backup bytes only when every current record still has
the migrated target digest. Any later edit blocks rollback rather than losing
new work. Restored older records intentionally require an older compatible Echel
version or a new migration preview; rollback is not silent reinterpretation.

Backups and migration journals are operational recovery state. They are not
canonical product knowledge, generated authority, or a substitute for Git.
Migration IDs are unique, backups are never overwritten, and no network or
Hermes runtime is required.
