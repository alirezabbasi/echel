# Findings, contradictions, and impact

A finding records an observed gap, contradiction, risk, defect, or unresolved
question. Agent and system observations may create an `open` finding with
provenance, but they cannot silently rewrite the knowledge or work that the
finding challenges.

`FindingService.preview_create(...)` validates the finding and every affected
canonical endpoint, then previews one durable transaction containing the finding
and explicit `affects` relationships. Applying the creation uses the transaction
journal, so interruption rolls back before commit or rolls forward after a
durable commit decision. Affected identifiers are not duplicated inside the
finding record.

Impact is a disposable projection reconstructed from the current finding and its
canonical relationships:

- active `error` or `critical` findings block maturity use;
- active `warning` findings add caution without a universal block;
- active `info` findings add notice;
- `resolved` and `dismissed` findings have no active impact;
- an `accepted` finding remains active—it acknowledges the issue rather than
  resolving it.

Only a human principal with `finding:decide` may accept, resolve, or dismiss a
finding. Each decision records the actor, capability, rationale, timestamp, and
reviewed finding revision. Optimistic concurrency prevents parallel decisions
from overwriting one another. Resolution changes the finding revision only;
changes to affected knowledge require their own proposal and authority workflow.

Finding kinds are deliberately small: `contradiction`, `risk`, `gap`, `defect`,
and `question`. Severity is `info`, `warning`, `error`, or `critical`. Product or
methodology-specific maturity policy may interpret caution more strictly later,
but must not mutate canonical records from a projection.

Schema-v1 finding records that used the earlier inline `affects` field must move
those references into explicit relationship records. Closed findings also need
human decision evidence. E2-022 owns general migration mechanics. Rollback must
preserve already-recorded findings and relationships; it must not restore impact
by rewriting affected source records.
