# Echel

Echel is progressive SDLC memory for AI-native software engineering.

It starts with one raw idea, asks only the questions required by the current stage, and lets product knowledge mature alongside implementation. Echel supplies an AI agent with the smallest trustworthy context needed for a work item and promotes verified discoveries back into durable project memory only after approval.

Echel owns methodology and product truth. Hermes is the first supported multi-model agent runtime; it owns sessions, tools, delegation, and model execution.

The accepted [Echel 2 product contract](docs/product/product-contract.md) defines both greenfield product creation and existing-project evolution, target audiences, responsibility boundaries, core scope, and explicit non-goals. The [ubiquitous language](docs/product/ubiquitous-language.md) gives every public Echel term one stable meaning and maps overloaded v1 language.

The [greenfield reference journey](docs/product/greenfield-reference-journey.md) and [brownfield reference journey](docs/product/brownfield-reference-journey.md) define reproducible end-to-end scenarios used to design and evaluate progressive product creation and existing-product evolution.

The [responsibility and authority contract](docs/product/responsibility-matrix.md) assigns one authoritative owner to every critical capability and defines how Echel interacts with humans, Hermes, Git, CI, and deployment systems.

The [benchmark suite](docs/product/benchmark-suite.md) selects three greenfield and three brownfield scenarios used to compare Echel’s methodology, context quality, execution portability, and long-term learning.

The [evaluation metric specification](docs/product/evaluation-metrics.md) defines reproducible context, task-success, rework, onboarding, evidence, safety, and cost measurements for those scenarios.

Foundational architecture choices are recorded in the [architecture decision index](docs/decisions/README.md), with consequences and replacement conditions kept explicit.

Contributors should begin with [CONTRIBUTING.md](CONTRIBUTING.md); the complete [task-packet workflow](docs/contributing/task-workflow.md) and [task template](docs/contributing/task-packet-template.md) define how work is selected, executed, verified, reviewed, and accepted.

The [quality baseline](docs/contributing/quality.md) documents local and CI checks across supported Python versions.

The [core record schema reference](docs/reference/core-schemas.md) defines Echel’s versioned canonical entity contracts and forward-compatible extension rules.

The [domain value-object reference](docs/reference/domain-value-objects.md) documents typed identifiers, revisions, confidence, status vocabularies, and stable validation failures.

The [canonical repository layout](docs/reference/canonical-repository-layout.md) defines safe project discovery and the repository-owned record collections.

The [canonical record-write contract](docs/reference/canonical-record-writes.md) defines validation, preview, deterministic serialization, and atomic replacement.

The [multi-record transaction journal](docs/reference/multi-record-transactions.md) defines deterministic commit, rollback, and crash recovery.

The [optimistic-concurrency contract](docs/reference/optimistic-concurrency.md) prevents stale agents and direct edits from silently overwriting newer knowledge.

## Why Echel changed

The first implementation proved that lifecycle knowledge, agent work packets, traceability, and verification could be connected. It also created the entire SDLC documentation structure upfront and represented the same truth through wiki pages, graph files, memory records, reports, and compatibility views. The machinery grew faster than the product knowledge it was meant to support.

Echel v2 returns to the original principle: begin with the minimum structured information and add knowledge only when the project learns something. The methodology remains; its implementation is now progressive instead of template-driven. Generic agent responsibilities move behind runtime adapters so Echel can concentrate on durable product meaning, context, and evidence.

See [Why Echel v2](docs/v2-reset.md) for the audience, rationale, continuity, and tradeoffs behind the reset.

## Lifecycle

```text
Idea → Problem → Vision → Strategy → Requirements → Domain → Architecture
→ Roadmap → Execution plan → Tasks → Repository → Implementation
→ Validation → Deployment → Operations and evolution
```

Stages are maturity states, not pre-created documentation folders. A project receives a new record only when it learns something. It advances when current knowledge is usable for the next decision, and later evidence may revise any earlier stage.

## Quick start

Echel has no runtime dependencies beyond Python 3.11.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .

mkdir my-product && cd my-product
echel init "My Product" --idea "A concise raw idea"
echel status
echel advance
echel add problem "The observed problem" --status accepted --confidence high
echel add user "The person affected by the problem" --status accepted
echel status
```

Create bounded work and compile its context:

```bash
echel work "First experiment" \
  --objective "Test the highest-risk assumption" \
  --relates-to CLM-001 \
  --accept "The assumption has a measurable result" \
  --verify "python3 -m unittest discover -s tests"

echel context WORK-001
echel run WORK-001                 # safe Hermes command preview
echel run WORK-001 --execute       # invoke Hermes
echel verify WORK-001
```

All durable product state lives under `.echel/` as small, reviewable JSON records. Generated indexes and agent conversation memory are not product truth.

## Design boundaries

- Echel owns product knowledge, lifecycle maturity, work context, provenance, and verification policy.
- Hermes owns the agent loop, multi-LLM execution, tools, sessions, and bounded delegation.
- Git owns version history and isolated implementation work.
- CI and deployment systems own authoritative build and release execution.
- Agent-proposed knowledge changes require review before becoming accepted truth.

See [Architecture](docs/architecture.md), [Methodology](docs/methodology.md), and [Hermes integration](docs/hermes.md).

## Development

```bash
python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m echel.cli.main lifecycle
```

The previous implementation is preserved locally in ignored `v1/` and is not part of the new source tree.
