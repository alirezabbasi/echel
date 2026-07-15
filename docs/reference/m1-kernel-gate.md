# M1 kernel performance and recovery gate

G-M1/v1 freezes and measures the performance, scale, projection, and recovery
properties required to let the greenfield and brownfield workflow milestones
build on the canonical kernel. The executable specification and deterministic
dataset generator live in [`benchmarks/kernel`](../../benchmarks/kernel/README.md).

The performance dataset contains 100,000 knowledge records and 1,000,000
canonical relationship records plus their traversal rows, deterministic FTS
content, and a reproducible generator digest. The gate
requires p90 indexed status, full-text, and reverse-link queries below 200 ms
over at least 25 samples. It captures build time and database size without using
them as portable thresholds on unnormalized hardware.

Recovery evidence covers the M1 mutation boundaries:

| Boundary | Required outcome | Evidence |
| --- | --- | --- |
| Single record | interrupted replacement preserves a valid old or new record | E2-014 atomic-write tests |
| Multi-record transaction | prepared intent rolls back; committing intent rolls forward | E2-015 recovery tests and G-M1 integration test |
| Migration | exact backup; prepared rollback; committing roll-forward; guarded restore | E2-022 migration tests |
| Projection | corruption is discarded; rebuild returns equivalent queries without touching truth | E2-023 and G-M1 integration tests |
| Portable import | invalid/tampered preview causes no canonical mutation; apply uses transaction recovery | E2-025 and G-M1 integration tests |

Passing G-M1 means these declared deterministic scenarios all recover without
lost authority or duplicate canonical effects (`RECOVERY = 1.00`). It does not
mean every future adapter, workflow, or runtime recovery path is already tested.

The selected six product scenarios are not yet materialized or validated and
are not cited as executed evidence. G-M1 also does not claim context compilation,
model quality, user outcomes, cross-platform performance, or Echel 2 release
readiness. Those remain governed by their downstream benchmark and release
tasks. The gate report is reproducible evidence, not canonical product truth.
