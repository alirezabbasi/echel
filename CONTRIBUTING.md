# Contributing to Echel

Echel welcomes focused contributions that improve a demonstrated workflow while preserving the project’s product contract and architecture decisions.

## Before starting

1. Read the [product contract](docs/product/product-contract.md), [ubiquitous language](docs/product/ubiquitous-language.md), and [architecture decisions](docs/decisions/README.md).
2. Select a ready task whose dependencies are accepted, or propose a task using the [task-packet template](docs/contributing/task-packet-template.md).
3. Confirm ownership with maintainers before implementation. Do not infer permission to change product authority, security policy, release state, or external systems.
4. Read the full [task-packet workflow](docs/contributing/task-workflow.md).

The private `echelit/` planning workspace is intentionally ignored and is not part of the public contribution contract. Public contributors work from an approved issue/task packet supplied through the repository’s collaboration channel.

## Working agreement

- Start from the minimum change that demonstrates the task outcome.
- Preserve one source of product truth; generated projections and agent/runtime memory are not authoritative.
- Keep Hermes/provider behavior behind runtime adapters.
- Do not combine unrelated refactoring with task work.
- Never add secrets, real personal data, proprietary inputs, or unreviewed generated dependencies.
- Preserve user changes in a dirty worktree and avoid destructive Git operations.
- Record discoveries as findings or proposed follow-up work instead of silently expanding scope.
- Add or update tests for accepted behavior and relevant failure/recovery paths.

## Required verification

Run the task-specific commands first, then the repository baseline:

```bash
make verify
git diff --check
```

Report exact commands and results. A passing command is evidence, not automatic acceptance.

Install the optional quality tools with `python -m pip install -e '.[quality]'` before running `make quality` or the individual typing, lint, packaging, and security targets. See the [quality baseline](docs/contributing/quality.md) for CI jobs, supported Python versions, and failure handling.

## Handoff

Use the [pull-request template](.github/PULL_REQUEST_TEMPLATE.md) or provide the same information with a patch:

- task ID and objective;
- implementation and affected contracts;
- acceptance mapping;
- verification evidence;
- compatibility, security, migration, and rollback impact;
- findings, exceptions, and proposed knowledge changes;
- reviewer decisions still required.

Maintainers may accept, request changes, reject, or split the contribution. Merge, release, deployment, and durable knowledge acceptance remain explicit human decisions.

## Community standards

Be precise, constructive, and respectful. Security-sensitive findings should follow the security reporting policy when published; until that policy exists, avoid public disclosure of exploitable details and contact a maintainer privately.
