# Architecture decision records

This directory contains accepted Echel 2 architecture decisions. ADRs record durable boundaries and tradeoffs; they do not replace the product contract, ubiquitous language, schemas, or implementation documentation.

| ADR | Decision | Status |
| --- | --- | --- |
| [ADR-0001](0001-repository-owned-canonical-records.md) | Repository-owned canonical records | Accepted |
| [ADR-0002](0002-disposable-projections-and-indexes.md) | Disposable projections and indexes | Accepted |
| [ADR-0003](0003-runtime-neutral-execution-protocol.md) | Runtime-neutral execution protocol | Accepted |
| [ADR-0004](0004-local-first-core-and-external-authority.md) | Local-first core and external authority | Accepted |
| [ADR-0005](0005-versioned-isolated-extension-contracts.md) | Versioned, isolated extension contracts | Accepted |

## ADR lifecycle

- **Proposed:** under review and not yet constraining implementation.
- **Accepted:** constrains downstream design and implementation.
- **Superseded:** retained for history and linked to its replacement.
- **Deprecated:** still applicable to existing versions but prohibited for new work.
- **Rejected:** considered but not adopted.

An accepted ADR is immutable except for typo fixes, clarifying links, and status metadata. A semantic change creates a new ADR that supersedes the old one. Each ADR must state context, decision, consequences, alternatives, failure/recovery behavior, and replacement conditions. Implementation discoveries that challenge a decision become findings or proposals; code does not silently rewrite the decision.

These ADRs deliberately stop before choosing schema details, exact directories, database tables, transport encoding, UI framework, hosted topology, or plugin packaging. Those choices require their downstream task evidence.
