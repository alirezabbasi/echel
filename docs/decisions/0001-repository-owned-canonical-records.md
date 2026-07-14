# ADR-0001: Repository-owned canonical records

- Status: Accepted
- Date: 2026-07-15
- Decision owners: Echel maintainers
- Depends on: product contract and ubiquitous language v1
- Supersedes: Echel v1’s overlapping wiki, graph, memory, report, and compatibility representations

## Context

Echel must preserve product intent, observations, assumptions, decisions, work, evidence, and learning across models, runtimes, sessions, and contributors. Users need local ownership, understandable diffs, backup through ordinary repository practices, and the ability to inspect or recover state without a hosted service.

Echel v1 represented related truth in several structures. That made navigation rich but created ambiguous authority, synchronization logic, and failure modes. A database-only store would simplify some queries while making Git review, portability, recovery, and external-tool interoperability harder.

## Decision

Canonical Echel product knowledge is stored as small, typed, versioned, repository-owned records colocated with the product under an Echel-managed directory.

- Each knowledge item has one canonical record identity and one current authoritative representation.
- Records use deterministic, schema-validated structured serialization suitable for review and migration. E2-011 selects exact schemas and E2-013 selects the final layout.
- Records carry schema version, stable ID, revision, state, provenance, timestamps, and explicit relationship references appropriate to their type.
- Mutations are made only through Echel’s storage/application boundary with validation, authority, concurrency, and atomicity policy. Editing a file externally is detectable input, not a bypass of validation.
- Git owns file and repository history. Echel owns record semantics and revision/concurrency rules. A Git commit does not automatically accept product knowledge.
- Secrets, large binaries, raw telemetry, model transcripts, generated reports, indexes, and external-system state are not canonical product records; safe references may be.
- A project can be opened, validated, migrated, and exported without a database server or hosted Echel account.

The initial implementation favors one independently addressable record per file because it limits conflict scope and makes recovery understandable. Packing, compaction, or an alternate backend requires measured need and must preserve the same logical contract and canonical export.

## Consequences

Benefits:

- one inspectable source of product truth;
- ordinary Git backup, review, branching, and portability;
- independent record validation and limited merge conflicts;
- deterministic recovery and migration without reconstructing runtime memory.

Costs:

- multi-record mutations need an explicit transaction/recovery mechanism;
- direct filesystem edits and Git merges can introduce invalid or conflicting revisions;
- large projects need disposable indexes for efficient query;
- file count and serialization overhead may eventually require compaction.

## Failure and recovery

- A failed single-record write leaves either the previous valid record or the complete new record, never a partial record.
- Multi-record mutation intent and recovery state are durable before canonical files diverge.
- Unknown schema versions fail with an actionable compatibility error; they are never rewritten opportunistically.
- Import, repair, and migration preview all affected records and preserve a rollback or forward-recovery path.
- Corrupt records are quarantined or reported with identity/path evidence; Echel does not fabricate replacements.
- Canonical state can reconstruct every projection and index without Hermes or network access.

## Alternatives considered

- **SQLite as the canonical store:** strong transactions and queries, but opaque Git diffs and awkward branch/merge behavior. Rejected for core authority; accepted as a disposable index.
- **Markdown documents as canonical truth:** pleasant for humans but weak typing, ambiguous partial edits, and hard machine evolution. Rejected; Markdown can be a projection or an explicitly typed contract.
- **Event log only:** excellent audit history but costly reconstruction, compaction, and user comprehension for the initial product. Deferred until evidence requires it.
- **Remote service as canonical authority:** enables collaboration but violates local-first ownership and creates availability/deployment complexity. Rejected for Echel 2 core.
- **Git itself as the domain model:** Git versions bytes but does not express record state, authority, provenance semantics, or lifecycle policy. Rejected.

## Replacement conditions

Revisit physical storage only when benchmark or production evidence shows repository records cannot meet measured scale, concurrency, integrity, or usability needs. A replacement must retain repository-owned canonical export, stable identities, provenance, offline recovery, deterministic migration, and the authority boundary. It requires a superseding ADR and compatibility plan.
