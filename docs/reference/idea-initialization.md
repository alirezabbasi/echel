# Idea-mode initialization

`echel init NAME --mode idea --idea TEXT --owner user:ID` creates the smallest
truthful greenfield state. The default `prototype` profile can be replaced with
`product`, `production`, or `regulated`; repeated `--config key=value` arguments
capture only settings already known to be required.

Initialization creates exactly two canonical records:

1. a project identity at maturity `idea`, with mode, profile, provenance, and a
   `dev.echel.initialization` extension containing the external owner reference,
   empty-or-explicit config, and `idea-init/v1` contract; and
2. one `raw-idea` claim containing the owner's exact trimmed input as a proposed
   claim at the idea stage.

The owner reference identifies the human responsible for product decisions; it
does not silently grant or record acceptance authority. The raw idea's
`confidence: 1.0` means Echel is confident this is the owner's captured input,
not that the idea is validated, viable, or true. Its `proposed` status preserves
that distinction.

No problem, user, vision, market claim, strategy, requirement, domain model,
architecture, roadmap, work item, task, policy file, documentation skeleton, or
agent/runtime state is created. Empty canonical collection directories and the
cache directory are storage layout, not knowledge.

`--dry-run` validates and explains the project ID, idea ID, owner, profile,
config, record list, digest, and next action without creating `.echel/`. Apply
builds the complete store in a temporary sibling directory, schema-validates and
writes both records there, then atomically publishes `.echel`. Invalid input,
unsupported profiles, non-user owners, duplicate or malformed config, likely
secret material, reinitialization, plan tampering, and interrupted publication
leave no partial project.

Idea initialization must run at an existing Git repository root. Config values
are ordinary non-secret strings; secret-like keys and common credential formats
are rejected. Secrets belong in an external secret manager, with only a safe
reference added later when a demonstrated workflow requires it.
