# Lifecycle maturity and backward revision

Lifecycle stages describe the uncertainty currently being reduced; they are not
document folders or a one-way waterfall. `LifecycleService.assess(...)` reads the
project's current maturity, the stage's minimum required claim kinds, accepted
canonical claims, active findings, and explicit `affects` relationships. Its
result explains missing knowledge, blocking findings, cautions, and the next
stage without changing repository state.

Forward advance is deliberately small. The current stage must have its minimum
accepted claims and no active `error` or `critical` finding affecting those
claims. Warning and info findings remain visible as cautions. A human holding
`lifecycle:advance` previews and applies the next adjacent maturity transition;
the project records actor, rationale, time, previous/next stage, and reviewed
revision. Agents cannot advance maturity, and optimistic concurrency prevents a
stale transition from overwriting a newer project revision.

Later evidence does not move the project cursor backward. Instead, an active
finding may trigger an explicit backward knowledge revision. A human holding
`knowledge:decide` selects an accepted protected root that the finding directly
affects. Echel previews the root plus accepted protected knowledge reachable via
directional `informs` or `supports` relationships, then marks that bounded set
`stale` in one recoverable transaction. Each revised record keeps its original
content and authority evidence while adding staleness provenance.

Stale knowledge no longer satisfies maturity requirements. Replacing it requires
a new proposal and the ordinary knowledge-authority workflow. No inferred graph,
project rollback, or automatic rewrite is permitted. Relationships not carrying
an explicit propagation meaning do not participate.

Schema-v1 claims now require `kind` and `stage`; project maturity uses the fixed
methodology vocabulary; stale protected records carry reviewed staleness
evidence. Existing records missing these fields need migration under E2-022.
Rollback must preserve revision history and must not fabricate acceptance or
silently clear findings.
