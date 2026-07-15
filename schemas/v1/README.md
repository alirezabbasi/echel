# Echel canonical record schemas v1

`src/echel/schemas/v1/record.schema.json` is the packaged authoritative structural
contract for Echel 2's twelve canonical record types. Validate records through `echel.schemas.SchemaRegistry` so
unsupported versions and unknown record types produce stable error codes.

The schema is intentionally structural. Cross-record references, lifecycle
transitions, authority, chronological ordering, and secret detection belong to
application policy and later kernel tasks.
