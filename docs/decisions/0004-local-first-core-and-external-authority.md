# ADR-0004: Local-first core and external authority

- Status: Accepted
- Date: 2026-07-15
- Decision owners: Echel maintainers
- Depends on: ADR-0001 and responsibility and authority contract v1
- Supersedes: assumptions that a hosted control plane is required for normal operation

## Context

Echel’s value is durable project knowledge and methodology continuity. Requiring a hosted service would add identity, tenancy, synchronization, privacy, availability, and operating-cost concerns before product value is validated. At the same time, real engineering relies on Git hosts, CI, deployment, secret, tracker, and telemetry systems that retain their own authority.

## Decision

Echel 2 core is local-first and useful offline. A repository can initialize, validate, inspect, evolve knowledge, plan work, compile tasks/context, preview runtime dispatch, import evidence, and render views without an Echel account or hosted Echel service.

- Core dependencies run on supported local platforms and store project state in the repository.
- Network access is denied by default for analysis and execution policy unless an operation declares and receives it.
- External integrations are optional adapters. Their unavailability degrades the bounded capability, not canonical project access.
- Git, CI, artifact, deployment, secret, telemetry, identity, and collaboration systems remain authoritative for their raw state. Echel stores safe immutable references, interpretations, and decisions.
- Secrets and raw sensitive telemetry never enter canonical records or ordinary context bundles.
- Synchronization previews direction, scope, conflicts, and external effects. No background synchronization silently accepts product knowledge.
- A future hosted service may coordinate or mirror projects but cannot become mandatory or silently supersede repository authority without a new product decision.

Local-first does not mean single-user forever. Collaboration uses Git and explicit external adapters first; validated demand may justify coordination services later.

## Consequences

Benefits:

- low onboarding and operational dependency;
- repository ownership, privacy, inspectability, and offline recovery;
- external systems can be replaced without migrating product meaning;
- hosted enterprise complexity remains demand-driven.

Costs:

- cross-device and multi-user coordination initially relies on Git and external systems;
- local environment differences require diagnostics and reproducibility controls;
- connectors need caching, staleness, and reconciliation semantics;
- some provider/runtime capabilities remain unavailable offline.

## Failure and recovery

- Network or connector failure preserves last known references with explicit staleness and never fabricates current status.
- Local operations that require external authority stop with an actionable unavailable/permission error or produce a preview only.
- Sync retries are idempotent where the external system supports it and otherwise require reconciliation.
- Local cache loss cannot destroy canonical records; external raw state is re-fetched from its owner.
- Repository conflicts use record-aware diagnostics and human resolution rather than last-write-wins.
- Credential absence or denial never causes credentials to be persisted in project knowledge.

## Alternatives considered

- **Hosted-first SaaS:** convenient collaboration but premature multi-tenancy, privacy, availability, and cost complexity. Deferred.
- **Fully standalone with no integrations:** simple but cannot relate authoritative delivery evidence. Rejected.
- **Copy all external state into Echel:** improves offline access but creates split authority and sensitive-data risk. Rejected.
- **Peer-to-peer synchronization:** local ownership but high conflict, identity, and security complexity without validated demand. Deferred.

## Replacement conditions

A hosted or coordination service becomes a core dependency only after validated user evidence, a product-contract revision, threat model, offline/export guarantee, migration plan, and superseding ADR. Individual optional connectors do not require an ADR when they preserve this authority boundary.
