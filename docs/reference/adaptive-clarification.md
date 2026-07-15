# Adaptive clarification contract

`clarification/v1` selects one material question from the gaps between current
canonical knowledge and the minimum problem-definition inputs. It is a
deterministic, read-only methodology projection: it creates no question log,
conversation memory, claim, or generated authority.

For an idea project, Echel checks for active `affected-actor`, `problem`,
`problem-context`, and `problem-observation` claims in that order. Proposed and
accepted claims prevent a repeated question; rejected, superseded, and stale
claims do not satisfy a gap. Each returned question includes a stable ID, the
claim kind an answer could inform, the reason the gap matters, and the exact
raw-idea record revision on which it is based.

```bash
echel --root . clarify
echel --root . --json clarify
echel --root . clarify --exclude problem.affected-actor
```

`--exclude` is request-scoped interruption/defer state. Callers can pass IDs
already asked in the current interaction without writing runtime conversation
state into product memory. Restarting without exclusions reconstructs the same
question from canonical records. An answer is not persisted by this contract;
the problem-definition workflow owns proposal, provenance, review, and
acceptance behavior.

When all remaining gaps are excluded, the result has no question but continues
to report unresolved claim kinds. This means “nothing else to ask in this
interaction,” not that the problem is mature. Invalid repositories, missing or
duplicate raw ideas, and unknown question IDs return stable
`ECHEL-CLARIFY-*` errors with a remedy and make no mutation.

The fixed ordering is intentionally small. A future methodology version may
add risk-sensitive policies after benchmark evidence demonstrates a need; an
LLM must not infer gaps or silently create product truth in this contract.
