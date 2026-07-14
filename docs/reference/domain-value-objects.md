# Domain value objects

Echel validates small semantic values before they reach storage, schema adapters,
or a runtime. `echel.domain` provides immutable value objects for identifiers,
revisions, confidence, and record-specific status.

- `Identifier("claim:need")` preserves both the complete reference and its
  `claim` namespace. It follows the exact syntax and length contract in schema v1.
- `Revision(1)` accepts only positive integers. Booleans are rejected even though
  Python treats them as integers.
- `Confidence(0.8)` normalizes numeric input to a float in the inclusive range
  zero through one. Confidence remains metadata and never grants authority.
- `RecordStatus("claim", "proposed")` validates status within that entity's
  lifecycle; a status valid for a run is not automatically valid for a claim.

Failures raise `DomainValidationError` with a stable code, field, and explanatory
detail. These types contain no persistence, JSON, workflow, or Hermes behavior.
Schema validation remains necessary at serialization and repository boundaries.
