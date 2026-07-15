# Lifecycle policy profiles

Echel uses one lifecycle for every project. Profiles change the minimum evidence
and control claims required at selected stages; they do not create separate
methodologies, repositories, document trees, or agent workflows.

The four built-in `v1` policies are cumulative in intent:

- `prototype` uses only the base lifecycle minimums to test an idea cheaply;
- `product` adds non-goals, acceptance, architectural constraints, and test
  evidence;
- `production` adds security, ownership, rollback, observability, and incident
  readiness;
- `regulated` adds generic data classification, traceability, threat modeling,
  audit evidence, approval, and retention claims.

`ProfileService.inspect(...)` returns the selected profile, assurance statement,
and effective requirements for every lifecycle stage without mutation. The
lifecycle maturity assessment uses that same policy and reports the selected
profile, policy version, required kinds, and any missing kinds.

Only a human holding `profile:change` may change a project's profile. Preview
shows the new policy and leaves state untouched. Apply records actor, rationale,
timestamp, prior/next profile, and reviewed project revision. Optimistic
concurrency prevents a stale profile decision from overwriting newer project
state. A change does not rewrite existing claims or move lifecycle maturity; it
only changes which minimums the next assessment applies.

The `regulated` profile is a generic rigor floor, not a certification, legal
opinion, or jurisdiction-specific compliance pack. Domain-specific controls,
policy packs, evidence exports, and formal assurance remain later reviewed
capabilities. Every inspection explicitly reports `certification: false`.

Schema-v1 project records now require a known profile. Existing projects without
one require an explicit migration choice under E2-022. Rollback preserves the
project revision and profile-decision evidence; it must not silently weaken a
selected policy or delete knowledge created to satisfy it.
