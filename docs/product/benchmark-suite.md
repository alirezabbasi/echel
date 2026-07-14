# Echel 2 benchmark suite

## Control

- Suite version: 1
- Product version: Echel 2
- Status: proposed for benchmark-selection review
- Authority: Echel maintainers
- Last reviewed: 2026-07-15
- Depends on: [Greenfield reference journey](greenfield-reference-journey.md) and [brownfield reference journey](brownfield-reference-journey.md)
- Machine-readable catalog: [`benchmarks/scenarios/index.json`](../../benchmarks/scenarios/index.json)

This contract selects six reproducible scenarios for design evaluation, regression testing, pilot comparison, and the Echel 2 benchmark. It fixes scenario intent and baseline knowledge without fixing metric thresholds, which belong to E2-007.

## Why authored fixtures

All six fixtures are authored for Echel and licensed under Apache-2.0. Brownfield fixtures model realistic repositories but do not copy third-party code or depend on a moving public repository. This gives Echel:

- immutable, redistributable inputs with no network dependency;
- controlled Git histories, defects, contradictions, and undocumented regions;
- stable ground truth for measuring observation and inference precision;
- freedom to publish expected answers without contaminating an external project;
- small enough repositories for local and community benchmark runs.

This choice sacrifices some ecosystem realism. The release benchmark must therefore supplement these controlled fixtures with disclosed real-project pilots; pilot results cannot be merged into controlled scores without being reported separately.

## Selected portfolio

| ID | Mode | Product shape | Primary challenge | Baseline |
| --- | --- | --- | --- | --- |
| GF-01 | Greenfield | Collaborative web workflow | Progressive discovery and bounded MVP | Raw idea, stakeholder evidence envelope, hidden evaluation oracle |
| GF-02 | Greenfield | Local-first CLI/data tool | Privacy, deterministic processing, and usability without a service | Raw idea, sample-data constraints, hidden evaluation oracle |
| GF-03 | Greenfield | Hosted developer API | Reliability, security, tenancy, and scope control | Raw idea, operational constraints, hidden evaluation oracle |
| BF-01 | Brownfield | Python CLI with SQLite | Recover architecture and change data behavior safely | Repository blueprint, Git-history shape, reviewed ground truth, change request |
| BF-02 | Brownfield | TypeScript HTTP service with PostgreSQL | Trace API/domain/persistence impact and compatibility | Repository blueprint, Git-history shape, reviewed ground truth, change request |
| BF-03 | Brownfield | Go event-processing service | Infer concurrency boundaries and plan an operationally safe change | Repository blueprint, Git-history shape, reviewed ground truth, change request |

The suite has three greenfield and three brownfield scenarios. Product shapes, languages, persistence, interfaces, risk profiles, and required reasoning differ; all converge on the same work-item, task-specification, runtime, evidence, and learning contracts.

## Scenario summaries

### GF-01 — Community shift coordination

Raw idea: help a small volunteer group coordinate recurring food-bank collection shifts without spreadsheets and message threads.

The benchmark evaluates whether Echel discovers the coordinator/volunteer distinction, validates missed or overbooked shifts, resists general volunteer-platform scope, and produces a vertical MVP whose decisions remain traceable. It is the canonical scenario from the greenfield reference journey.

### GF-02 — Private invoice anomaly review

Raw idea: give independent workers a local command-line tool that highlights likely mistakes in invoice CSV files before they send them.

The benchmark evaluates progressive clarification for non-technical users, privacy and offline constraints, deterministic evidence, explainable findings, malformed input, locale/currency ambiguity, and whether Echel avoids inventing accounting or fraud claims.

### GF-03 — Webhook delivery relay

Raw idea: let small SaaS teams send webhooks reliably without building retry infrastructure.

The benchmark evaluates hypothesis discipline, API and operational product thinking, tenant isolation, signing and secret boundaries, delivery semantics, observability, cost assumptions, and whether the first experiment remains smaller than a generalized event platform.

### BF-01 — Ledger CLI tagging

A Python 3.11 CLI imports transaction CSV files into SQLite, applies rule-based categories, and exports reports. Tests cover parsing and persistence, but architecture documentation is stale and Git history shows repeated changes around duplicate imports. The requested change adds batch tagging with undo.

The fixture tests safe ingestion, command discovery, data invariants, stale-document detection, transaction boundaries, migration/rollback reasoning, and incremental re-analysis.

### BF-02 — Appointment waitlist API

A strict TypeScript/Node HTTP service uses PostgreSQL migrations, a layered module structure, OpenAPI documentation, and integration tests. Documentation says full appointments reject bookings, while an unfinished branch and issue text imply waitlist intent. The requested change adds idempotent waitlist enrollment and promotion.

The fixture tests conflicting evidence, API compatibility, concurrency, persistence, authorization, migration impact, and separation of observations from inferred domain rules.

### BF-03 — Go delivery-event processor

A Go service consumes delivery events, deduplicates them in an embedded store, exposes health/metrics endpoints, and retries failed handlers. It has good unit tests but weak operational documentation and a known shutdown race in history. The requested change adds a bounded dead-letter replay command.

The fixture tests package-boundary inference, concurrency and cancellation reasoning, command/API discovery, operational safety, audit evidence, and impact across runtime and storage concerns.

## Baseline contract

Each scenario manifest has these required sections:

- stable ID, mode, version, title, lifecycle state, authorship, and SPDX license;
- product shape, risk focus, and required Echel capabilities;
- immutable input description and explicit exclusions;
- baseline facts or ground-truth observations, expected unknowns, and traps;
- target change or outcome and evaluation evidence;
- fixture materialization requirements and reproducibility controls.

Greenfield baselines contain the raw idea and a controlled discovery envelope. They do not contain accepted problem, strategy, requirements, domain, or architecture at initialization. Expected discoveries are evaluator oracles, not context supplied to the agent.

Brownfield baselines contain a repository blueprint and reviewed ground truth. During a benchmark run, Echel sees only the materialized repository and request; ground truth remains evaluator-only until a maintainer corrects or approves proposals. A repository snapshot is valid only when its manifest records the fixture generator version, Git head, tree digest, license digest, toolchain, and expected clean verification result.

## Materialization states

The M0 suite selects and versions the six scenario fixtures and their semantic baselines. Each manifest currently has lifecycle state `selected`. A brownfield fixture becomes `materialized` only after later implementation work creates its licensed Git snapshot and fills all non-null snapshot digests; it becomes `validated` only after an independent clean-room run reproduces its baseline. Greenfield fixtures become `validated` after the discovery scripts and evaluator oracles receive independent review.

No performance or release claim may cite a `selected` fixture as an executed benchmark result. This prevents scenario selection from fabricating measurements or pretending that future fixture repositories already exist.

## Fair-run protocol

1. Record Echel, runtime, model/provider, adapter, fixture, policy, and evaluator versions.
2. Begin from the manifest’s declared visible input; keep evaluator-only baseline fields unavailable to Echel, Hermes, and models.
3. Use a fresh local workspace with network denied unless the scenario explicitly measures network use.
4. Apply identical capability and budget policy across compared runs, or disclose the difference.
5. Capture prompts only as runtime diagnostics; canonical measurements use Echel task, context, event, evidence, and decision records.
6. Preserve failures, retries, human interventions, and excluded measurements.
7. Run clean verification before and after the target change and record Git state.
8. Score with E2-007; never tune expected answers after seeing a model’s result without a new suite version.

## License and data policy

Scenario manifests, future generated source fixtures, sample inputs, Git histories, and evaluator baselines are Echel-authored and Apache-2.0 under the repository license. Every manifest declares `Apache-2.0`; a materialized fixture must include a copy of the license and an attribution manifest.

Fixture data is synthetic. It must contain no real personal data, credentials, proprietary code, trademark-dependent branding, copied issue text, or live service endpoints. Secret-like test values must be conspicuously fake and recognized by fixture policy. Generated dependencies are not vendored; package lockfiles must retain their own license metadata.

A new third-party fixture requires a pinned source revision, verified license and attribution, redistribution analysis, dependency/license inventory, offline archive strategy, and maintainer approval. A URL and branch name are insufficient.

## Selection criteria and rejected alternatives

Selected scenarios jointly cover progressive discovery, repository recovery, CLI/web/API/event shapes, three implementation languages, local and hosted operation, relational and embedded persistence, security, concurrency, compatibility, operations, and backward learning.

Alternatives rejected for the controlled suite:

- **Only Echel’s own repository:** realistic but self-referential and narrow in language/domain coverage.
- **Six popular open-source repositories:** realistic but expensive, moving, license/dependency-sensitive, and vulnerable to model memorization.
- **Six generated toy CRUD apps:** reproducible but too shallow to measure uncertainty, architecture recovery, or operational impact.
- **One large enterprise simulation:** broad but slow, hard to reproduce locally, and likely to reward documentation volume.
- **Private customer repositories:** valuable pilots but not publishable or independently reproducible.

## Failure and maintenance rules

| Condition | Required action |
| --- | --- |
| Manifest is invalid, duplicate, or lacks a baseline/license | Exclude it; do not reduce the suite denominator silently |
| Fixture digest or Git head differs | Mark run invalid until the declared snapshot is restored or suite version changes |
| Toolchain is unavailable | Record unsupported run; do not substitute versions without disclosure |
| Evaluator oracle leaks into agent context | Invalidate the affected run and record the leak |
| Fixture contains a secret or non-synthetic personal data | Quarantine it, remove exposed history safely, rotate if needed, and release a new fixture version |
| License or provenance is disputed | Stop redistribution and benchmark publication until resolved |
| Baseline is shown to be wrong | Preserve the old version/results, record evidence, correct in a new suite version, and rerun comparisons |
| Model is known to have trained on a materialized fixture | Disclose contamination risk and compare against controlled variants or pilots |
| Runtime stops or permission is denied | Retain the failed attempt and measure recovery under the same scenario policy |
| Scenario becomes trivial due to implementation drift | Version or replace it through review; never silently expand hidden requirements |

## Acceptance and handoff

The suite selection is acceptable when all six manifests validate; exactly three are greenfield and three brownfield; every fixture is Echel-authored and Apache-2.0; baselines separate visible input from evaluator-only truth; the brownfield set varies language and product shape; and selection does not claim unexecuted results.

E2-007 consumes the catalog to define metrics and thresholds. Later greenfield, brownfield, context, runtime, delivery, and release milestones materialize or exercise the relevant fixtures. Any change to scenario meaning, visible input, ground truth, or license increments the suite or fixture version and invalidates direct comparison unless a migration is documented.
