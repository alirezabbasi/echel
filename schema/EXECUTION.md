# Execution Schema (v1)

This schema defines execution node behavior for tasks, stories, incidents, and RCA work. Product-level lifecycle stage readiness is defined separately in `schema/lifecycle-stage.schema.md`.

## Lifecycle states

`idea`, `discovery`, `design`, `build`, `verify`, `release`, `operate`

## Transition rules

- Forward transitions are default.
- Backward transitions are allowed only with a linked reason artifact (`incident` or `rca` or `decision`).
- A node cannot enter `release` without satisfying all `verify` closure gates.

## Typed node model

Required fields:

- `id`: unique identifier (example: `TASK-0042`)
- `type`: `epic | story | task | incident | rca`
- `title`: concise statement
- `state`: lifecycle state
- `owner`: accountable role or person
- `risk_class`: `low | medium | high | critical`
- `depends_on`: list of node IDs
- `context_links`: canonical wiki/doc links
- `acceptance_criteria`: explicit, testable outcomes
- `definition_of_done`: completion conditions
- `closure_gates`: list of gate IDs

Optional fields:

- `parent_id`
- `target_release`
- `labels`
- `updated_at`

## Closure contract

A node is closable only when:

1. Dependencies are closed.
2. Required evidence artifacts are present.
3. All closure gates pass.
4. Knowledge artifacts are updated.

## Canonical link policy

Every node must link to at least:

- one context source
- one standards/governance reference
- one verification command or evidence pointer
