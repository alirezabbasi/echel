# Echel

Echel is progressive SDLC memory for AI-native software engineering.

It starts with one raw idea, asks only the questions required by the current stage, and lets product knowledge mature alongside implementation. Echel supplies an AI agent with the smallest trustworthy context needed for a work item and promotes verified discoveries back into durable project memory only after approval.

Echel owns methodology and product truth. Hermes is the first supported multi-model agent runtime; it owns sessions, tools, delegation, and model execution.

The accepted [Echel 2 product contract](docs/product/product-contract.md) defines both greenfield product creation and existing-project evolution, target audiences, responsibility boundaries, core scope, and explicit non-goals. The [ubiquitous language](docs/product/ubiquitous-language.md) gives every public Echel term one stable meaning and maps overloaded v1 language.

The [greenfield reference journey](docs/product/greenfield-reference-journey.md) defines the first reproducible end-to-end scenario used to design and evaluate progressive product creation.

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
