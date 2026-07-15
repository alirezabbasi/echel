# Core record schemas

Echel's canonical knowledge is a set of small, independently addressable JSON
records. Version 1 defines twelve record types: project, claim, decision,
artifact, relationship, finding, work item, immutable task specification, run,
evidence, release, and learning. Their shared contract is
[`record.schema.json`](../../src/echel/schemas/v1/record.schema.json).

Every record carries a stable typed identifier, schema version, monotonically
increasing revision, timestamps, and provenance. The schema rejects unknown
top-level fields. Optional metadata belongs under `extensions`, whose keys must
be namespaced (for example `dev.echel.plugin`). Readers must preserve extension
values unchanged and must not interpret them as overrides of core fields.

Accepted or rejected claims, decisions, and learnings also carry the core
[authority evidence](knowledge-authority.md) for the exact proposal revision a
human reviewed. Runtime provenance never substitutes for this decision evidence.

Relationship records require existing typed endpoints, a predicate, a specific
reason, ordinary provenance, and the versioned policy that allowed the link.
See [explicit relationships](explicit-relationships.md).

## Compatibility policy

- `schema_version` is a major integer. Readers reject unsupported majors with
  `ECHEL-SCHEMA-VERSION-UNSUPPORTED`; they never guess or silently migrate.
- Additive metadata uses `extensions`, allowing older readers to round-trip data.
- Breaking field or semantic changes require a new version, explicit migration,
  preview, backup, and rollback. Migration infrastructure is delivered by E2-022.
- Schemas contain no defaults: omission is visible and deterministic.
- Stable errors distinguish load failure, unsupported version, unknown record
  type, and structurally invalid data.

JSON Schema validates record shape. Referential integrity, revision conflicts,
timestamp ordering, lifecycle transitions, authority, relationship cycles, and
secret detection are application invariants and are deliberately not duplicated
in this contract.
