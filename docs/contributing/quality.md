# Quality and CI baseline

## Control

- Baseline version: 1
- Product version: Echel 2
- Status: proposed for CI-baseline review
- Authority: Echel maintainers
- Last reviewed: 2026-07-15
- Workflow: [`.github/workflows/quality.yml`](../../.github/workflows/quality.yml)

The quality baseline makes repository changes reproducibly testable without turning CI into product authority. CI owns raw job execution and results; Echel and authorized reviewers decide whether that evidence satisfies a task or release policy.

## Supported Python

Echel supports CPython 3.11, 3.12, 3.13, and 3.14. Python 3.11 is the minimum declared by `pyproject.toml` and the tool-analysis baseline. Unit and integration/contract scenario suites run against every supported minor version. Packaging, typing, lint, and security jobs use the minimum version so new syntax or library behavior cannot silently raise the floor.

Changing the minimum or supported matrix requires compatibility evidence, documentation and packaging updates, a task/consumer impact review, and maintainer approval. A newly released Python version is not supported until CI passes and the matrix is explicitly revised.

## Jobs and evidence

| Job | Command or action | Purpose | Blocking |
| --- | --- | --- | --- |
| Unit | `make unit` on 3.11–3.14 | Fast domain/storage/context/runtime behavior | Yes |
| Scenarios | `make scenarios` on 3.11–3.14 | Integration journeys and M0 contract/scenario behavior | Yes |
| Typing | `make typing` on 3.11 | Static consistency for `src/echel` | Yes |
| Lint | `make lint` on 3.11 | Syntax/error/import-quality baseline for source and tests | Yes |
| Packaging | `make package-check`, clean wheel install, CLI smoke | Build metadata, sdist/wheel integrity, and installed entry point | Yes |
| Security | `make security` | Bandit medium/high-confidence source gate and installed-environment consistency | Yes |
| Dependency review | GitHub dependency review on pull requests | Reject newly introduced known-vulnerable dependency changes where GitHub supports it | Yes on pull requests when configured as required |
| Baseline | Job-result aggregation | One stable branch-protection check for all core jobs | Yes |

`make verify` remains the dependency-free local baseline: all tests, bytecode compilation, and CLI smoke behavior. `make quality` adds typing, lint, and security after installing optional quality tools. Packaging is separate because it creates ignored `build/` and `dist/` outputs.

## Local reproduction

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[quality]'

make verify
make typing
make lint
make security
make package-check
git diff --check
```

The quality dependency ranges are centralized under the `quality` optional dependency. CI installs only the tools needed by each isolated job, reducing privilege and diagnosis scope. Tool versions must be captured in CI logs; a future lock/hashing task may freeze exact transitive versions when reproducibility evidence justifies the maintenance cost.

## Workflow security and resource policy

- Workflow permissions default to `contents: read`; no job receives write, release, package, deployment, secret, or pull-request mutation authority.
- Checkout does not persist credentials.
- Jobs use supported GitHub-maintained action major versions and bounded timeouts.
- Pull requests never execute deployment or release behavior.
- Source tests require no network or project dependency installation.
- Quality tools execute against repository source but their output is evidence only; scanners cannot accept findings or mutate product knowledge.
- Bandit blocks medium/high-severity findings at medium-or-higher confidence. Low-severity findings remain review inputs and become explicit tasks when their threat context warrants change.
- Concurrency cancels superseded runs on the same ref, while GitHub retains their terminal evidence.
- Third-party action major updates and new actions require source/release review; security hardening may later pin immutable action commits.

## Failure, interruption, and recovery

| Condition | Treatment |
| --- | --- |
| One Python version fails | Compatibility fails; do not average or ignore the version |
| Tool installation or registry is unavailable | Job fails as infrastructure evidence; retry is explicit and the original failure remains visible |
| Job times out or is cancelled by a newer run | Terminal state remains non-success; rerun against the same revision or use the newer revision deliberately |
| Optional dependency review is unavailable on a fork or repository plan | Core security job still runs; maintainer records the missing external check rather than fabricating success |
| Scanner reports a finding | Preserve output, triage severity/exploitability, fix or record an authorized time-bounded exception |
| Packaging leaves artifacts locally | Remove/rebuild ignored artifacts; they are never canonical or committed |
| CI and local results disagree | Preserve both, compare revision/tool/environment, and open a finding; CI does not overwrite local evidence |
| Action/tool range drifts and changes results | Record versions, reproduce, then pin or revise the baseline through review |
| Required job is skipped | Aggregate baseline fails; skipped is not success |

Retries do not erase failures. An exception records owner, rationale, scope, evidence, expiry, and corrective task. Tests, typing, lint, or security rules must not be weakened merely to make a pre-existing failure green.

## Branch protection and review

Configure `required quality baseline` as the stable required check after the workflow has run on the repository. Dependency review may be separately required for pull requests when the repository supports it. Branch protection is external Git-host state and must be configured by an authorized maintainer; this task supplies the workflow but does not mutate repository settings.

A green baseline means declared checks succeeded for one revision. It does not prove product correctness, approve a task, merge a change, accept knowledge, authorize release, or authorize deployment.

## Non-goals and future strengthening

This baseline does not add coverage percentage gates, mutation testing, SAST vendors, SBOM/signing, reproducible lockfiles, multi-platform runners, release publication, deployment, or benchmark execution. These are added only by evidence-driven tasks. E2-100 owns the full threat model/security audit; E2-102 owns cross-platform packaging; E2-105 owns the release benchmark.

## Acceptance

The baseline is acceptable when unit and scenario behavior runs across every supported Python version; typing, lint, packaging/install, source security, and dependency-change checks are explicit; permissions are read-only and time-bounded; local reproduction is documented; failures/skips remain visible; and the aggregate check cannot report success when a required core job failed.
