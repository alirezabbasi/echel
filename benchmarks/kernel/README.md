# G-M1 kernel gate

G-M1 is the M1 engineering gate for the canonical knowledge kernel. Version 1
freezes these targets before measurement:

- a deterministic disposable projection holds 100,000 knowledge records plus
  1,000,000 canonical relationship records and their traversal rows;
- indexed status, FTS lookup, and reverse-link lookup each remain below 200 ms
  at p90 over at least 25 samples;
- canonical writes, multi-record transactions, migrations, disposable-index
  rebuilds, and portable import retain a 100% recovery result across their
  declared deterministic interruption scenarios;
- deleting and rebuilding a projection produces equivalent queries without
  changing canonical bytes.

Run the scale and latency measurement with:

```bash
PYTHONPATH=src python3 -m benchmarks.kernel.gate /tmp/echel-g-m1.sqlite3
```

The generator is deterministic and its specification digest is captured in the
report. Build duration and database size are observations, not gates, because
hardware classes are not normalized. The 200 ms threshold applies to local
indexed kernel queries, not full raw-file integrity inspection.

This synthetic dataset is valid performance evidence for the storage/index
kernel only. The six product scenarios remain `selected`, so G-M1 does not claim
greenfield or brownfield journey quality, context quality, agent success, model
performance, cross-platform equivalence, or release readiness. Those claims
belong to the downstream validated-scenario and release benchmark tasks.

The captured local execution under `evidence/2026-07-15-local.json` records its
exact Python, SQLite, platform, dataset digest, timings, build duration, size,
and limitations. It is reproducible measurement evidence, not a portable claim
that other hardware will produce identical timings.
