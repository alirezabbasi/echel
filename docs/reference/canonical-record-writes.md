# Canonical record writes

`CanonicalRecordStore` is the only Echel 2 filesystem boundary for writing one
canonical record. It validates the complete schema before deriving a path or
creating a temporary file. Invalid data therefore cannot partially mutate the
repository.

Call `preview_write(record)` to obtain the destination, record ID, content digest,
replacement state, and whether bytes would change. Preview performs no mutation.
Call `write(record)` to serialize deterministic UTF-8 JSON, flush and synchronize
the temporary file, then atomically replace the destination in the same directory.
If validation, writing, synchronization, or replacement fails, the temporary file
is removed and the previous complete record remains authoritative.

Record IDs use `namespace:local` form, but only the safe local component becomes
the filename inside its type-specific collection. The namespace must match the
record type. Project is the one singleton at `.echel/project.json`; all other core
types have collections under `.echel/records/`.

Identical content is a no-op. Revision-conflict detection is intentionally not
part of this boundary yet; E2-016 adds optimistic concurrency. The
[multi-record transaction journal](multi-record-transactions.md) coordinates
mutations spanning multiple records. Direct writes, runtime memory, and cache
content never become equivalent alternatives to this canonical path.
