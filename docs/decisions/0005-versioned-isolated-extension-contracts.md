# ADR-0005: Versioned, isolated extension contracts

- Status: Accepted
- Date: 2026-07-15
- Decision owners: Echel maintainers
- Depends on: ADR-0003 and responsibility and authority contract v1
- Supersedes: unrestricted in-process customization and fixed built-in agent-role assumptions

## Context

Echel cannot natively understand every language, repository, methodology variation, runtime, CI provider, deployment platform, or telemetry source. Extensibility is necessary, but a general plugin framework introduced before concrete extension types would create unstable APIs, dependency conflicts, secret exposure, and ways to bypass canonical authority.

## Decision

Echel extends through a small set of capability-specific, versioned contracts with deny-by-default permissions and isolation appropriate to risk.

Initial extension families are limited to demonstrated needs:

- repository analyzers;
- runtime adapters;
- evidence providers;
- repository blueprints;
- deployment/telemetry connectors; and
- deterministic renderers or import/export adapters.

Each extension declares identity/version, contract versions, capabilities, input/output schemas, permissions, filesystem/network/secret requirements, determinism and idempotency, cancellation, resource limits, compatibility, and provenance. Echel validates declarations before invocation and records extension identity with every output.

Extensions cannot:

- write canonical records directly or approve knowledge, policy exceptions, reviews, releases, or deployments;
- access undeclared paths, network, credentials, or tools;
- inject instructions into unrelated agent/runtime context;
- replace core schema validation, authority, provenance, transaction, or policy logic;
- make a project unreadable when the extension is absent; or
- introduce a new authoritative owner without revising the responsibility contract.

Prefer out-of-process or runtime-owned execution for untrusted and tool-using extensions. A small trusted built-in adapter may run in process only behind the same contract and tests. Echel 2 does not promise arbitrary third-party in-process Python plugins or a marketplace.

## Consequences

Benefits:

- ecosystem growth without a monolithic core;
- clear compatibility and security boundaries;
- extensions remain replaceable and testable with fixtures;
- absence/failure degrades one capability instead of corrupting product truth.

Costs:

- contract design, isolation, serialization, and compatibility overhead;
- less freedom than importing arbitrary application internals;
- duplicated adapters may require shared SDK tooling later;
- out-of-process execution has latency and packaging costs.

## Failure and recovery

- Missing or incompatible extensions fail discovery with the exact required/provided contract versions and alternatives.
- Invalid output, permission denial, timeout, crash, or cancellation produces a structured failure and cannot partially mutate canonical state.
- Repeated invocation uses an idempotency key where effects are possible; unknown external effects require reconciliation.
- Extension findings and inferred knowledge remain proposals with provenance.
- A quarantined or removed extension leaves canonical projects valid; derived outputs can be discarded and rebuilt by another compatible extension.
- Extension upgrades never migrate canonical state without an explicit Echel migration preview and approval.

## Alternatives considered

- **One universal plugin interface:** simple branding but hides distinct security, lifecycle, and data contracts. Rejected.
- **Arbitrary in-process Python entry points:** easy to build but share memory, dependencies, filesystem, secrets, and authority. Rejected for third-party extensions.
- **All functionality in core:** consistent but unmaintainable across ecosystems. Rejected.
- **Runtime skills as all Echel extensions:** useful for execution but makes methodology/storage/integration capability runtime-dependent. Rejected.
- **Marketplace in 2.0:** discoverable but requires trust, signing, review, distribution, support, and governance before demand. Deferred.

## Replacement conditions

Add a new extension family only after two concrete implementations demonstrate shared semantics and the security review defines its authority. A general SDK or registry may follow validated community use. Allowing direct canonical mutation, shared-process untrusted code, or mandatory proprietary extensions requires a superseding ADR and threat-model update.
