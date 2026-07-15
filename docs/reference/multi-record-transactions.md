# Multi-record transaction journal

Echel coordinates mutations spanning canonical records with a local durable
journal under `.echel/transactions/`. It does not claim that several filesystem
renames are physically atomic. Instead, it makes the commit decision explicit
and guarantees one deterministic recovery direction.

1. `preview` schema-validates every record, rejects duplicate destinations, and
   explains the proposed transaction without mutation.
2. `prepare` writes staged deterministic record bytes and a versioned manifest,
   then atomically installs the complete prepared journal.
3. `commit` durably changes the journal to `committing` before any canonical file
   changes. It then uses the single-record atomic writer for each staged record.
4. After every record is installed, the journal becomes `committed` and is
   removed. Leftover committed journals are safe cleanup work.

Recovery rolls back `prepared` transactions because no commit decision exists.
It rolls `committing` transactions forward because their intent is durable;
already-written identical records are no-ops. Staged digest or identity mismatch
halts recovery with evidence rather than guessing. An explicit rollback is only
allowed while prepared.

Transaction journals are operational recovery state, not product knowledge and
not an alternate source of truth. They do not accept records, confer authority,
or define revision conflicts. Optimistic concurrency is introduced by E2-016.
