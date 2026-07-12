---
type: guide
status: active
---
# Echel Technical Quick Start

This guide contains the technical setup, command reference, and operating model for Echel.

## Initialize A Project

```bash
make init-wizard
```

Non-interactive:

```bash
make init-project \
  NAME=my-project \
  MODE=scratch \
  DEST=. \
  PROBLEM="..." \
  SOLUTION="..." \
  DIRECTION="..." \
  USERS="..." \
  MVP="..." \
  CONSTRAINTS="..." \
  RISKS="..." \
  STACK="..." \
  SUCCESS="..."
```

Existing repository:

```bash
make init-project NAME=existing-project MODE=existing DEST=. SOURCE=/path/to/repo
```

Generated layout:

```text
<project-name>/
  wiki/          product-owned memory committed with the project
  echel-core/    Echel runtime, method, schemas, tools, prompts, and automation
```

`wiki/` belongs to the product repository. `echel-core/` is framework infrastructure and is ignored by the generated project repository.

## Validate Initialization

```bash
cd <project-name>/echel-core
make wiki-health
python3 tools/echel.py doctor
```

## Product Commands

```bash
python3 tools/echel.py define --problem "..." --solution "..." --direction "..."
python3 tools/echel.py clarify
python3 tools/echel.py clarify --field mvp --answer "- First useful slice"
python3 tools/echel.py plan
python3 tools/echel.py status
python3 tools/echel.py next
python3 tools/echel.py build
python3 tools/echel.py review
python3 tools/echel.py steer --field direction --value "..."
```

## Lifecycle Commands

```bash
python3 tools/echel.py discover
python3 tools/echel.py canon
python3 tools/echel.py strategy
python3 tools/echel.py requirements
python3 tools/echel.py readiness --stage requirements
python3 tools/echel.py domain
python3 tools/echel.py readiness --stage domain
python3 tools/echel.py architecture
python3 tools/echel.py readiness --stage architecture
python3 tools/echel.py execution-tasks
python3 tools/echel.py repository-factory
python3 tools/echel.py validate
python3 tools/echel.py evidence add --id EVID-VALIDATION-001 --subject TEST-001 --kind validation-report --path wiki/reports/validation-summary.md --producer "QA Agent" --summary "Validation summary proof"
python3 tools/echel.py readiness --stage release
python3 tools/echel.py learning
python3 tools/echel.py learning add --source-kind incident --title "..." --summary "..." --action task
```

Architecture artifacts live under `wiki/architecture/` after the domain gate passes. `GATE-ARCHITECTURE` must pass before roadmap work because it checks deployment posture, data/security/observability models, ADR coverage, requirement/domain mappings, graph coverage, and overengineering risk. The root `wiki/architecture.md` remains a compatibility summary for current graph and cockpit views.

Roadmap artifacts live under `wiki/roadmap/` after architecture readiness. The expanded roadmap surface includes master, MVP, architecture, engineering, and release roadmaps; the root `wiki/roadmap.md` remains a compatibility summary.

Execution phase artifacts live under `wiki/execution/` after roadmap expansion. The phase surface includes foundation, MVP, hardening, production, and evolution plans. `python3 tools/echel.py execution-tasks` converts each phase task row into a one-session `wiki/work/TASK-1xxx-*.md` task and maintains `wiki/work/TASK_INDEX.md`.

Repository factory artifacts live under `generated/product-repository/` after execution tasks exist. `python3 tools/echel.py repository-factory` creates the app, config, tests, CI skeleton, environment example, verification script, and generated local development docs from architecture and task inputs.

Product-owned engineering policy lives under `wiki/engineering/`. The generated repository README and local docs contain the exact setup, start, lint, test, and aggregate verification commands. Verify the generated baseline with:

```bash
cd generated/product-repository
python -m compileall -q app tests
python -m unittest discover -s tests
python app/main.py
./scripts/verify.sh
```

Validation artifacts live under `wiki/validation/`. They define test strategy, acceptance, integration, e2e, security, performance, and validation report surfaces that map tests to requirement IDs, task IDs, domain concepts, and acceptance criteria. `python3 tools/echel.py validate` summarizes those artifacts, writes `wiki/reports/validation-summary.md`, refreshes `wiki/validation/validation-report.md`, and adds validation test/evidence target nodes to the product graph. `python3 tools/echel.py evidence add` registers proof artifacts in `.echel/evidence_registry.json` with subject, kind, path, checksum, producer, and summary, then refreshes graph evidence nodes for task closure and release proof.

Deployment artifacts live under `wiki/deployment/`. They define deployment architecture, environments, release process, rollback plan, secrets management, and production checklist inputs for the release gate. `python3 tools/echel.py readiness --stage release` blocks production readiness when validation blockers, deployment docs, rollback, checklist rows, registered evidence, or release risks are unresolved.

Operations artifacts live under `wiki/operations/`. They define the runbook, observability signals, incident severity and escalation, backup and recovery, SLA/SLO expectations, change management, and evolution backlog used for post-release support and learning-loop handoff.

The learning loop is captured by `python3 tools/echel.py learning add`. It records incidents, RCA, customer feedback, roadmap changes, and strategy changes into `wiki/operations/learning-records.md`, then routes follow-up into tasks, ADRs, risks, assumptions, or strategy-change memory depending on the selected `--action`.

## Graph And Memory Commands

```bash
python3 tools/echel.py graph build
python3 tools/echel.py graph validate
python3 tools/echel.py graph report
python3 tools/echel.py traceability
python3 tools/echel.py feature add --title "..."
python3 tools/echel.py risk add --title "..." --mitigation "..."
python3 tools/echel.py link --from <node-id> --to <node-id>
```

`python3 tools/echel.py traceability` writes `wiki/reports/traceability-matrix.md`, showing the lifecycle chain from discovery through evidence and highlighting missing canon or evidence links.

## Readiness Commands

```bash
python3 tools/echel.py milestone --name "MVP" --kind release
python3 tools/echel.py readiness --target mvp
python3 tools/echel.py proof-pack --target mvp
python3 tools/echel.py release-summary --target mvp
```

## Operator Commands

```bash
python3 tools/echel.py start
python3 tools/echel.py doctor
python3 tools/echel.py close-task TASK-0001
python3 tools/echel.py sync-memory
python3 tools/echel.py conformance run
python3 tools/echel.py migration plan
python3 tools/echel.py workspace move --dry-run
python3 tools/echel.py workspace move --apply
```

## Product Cockpit

Initialize and run the local cockpit:

```bash
python3 tools/echel.py platform init
python3 tools/echel.py platform up --host 127.0.0.1 --port 8787
```

Open:

```text
http://127.0.0.1:8787
```

The cockpit is organized around the Echel lifecycle: Discovery, Canon, Strategy, Requirements, Domain, Architecture, Roadmap, Execution, Build, Validate, Release, Operate, and Governance. The header always shows the current stage, responsible AI role, blocker count, and next action; each stage embeds relevant artifact context and guided command-backed actions such as answering discovery fields, generating canon/strategy/requirements/domain/architecture artifacts, creating work packets, registering evidence, recording learning, and running readiness or governance reports.

## Verification

```bash
make verify-phase1
make verify-phase2
make verify-phase3
make verify-phase4
make verify-phase5
make wiki-health
python3 tools/echel.py doctor
python3 tools/echel.py conformance run
python3 tools/echel.py graph validate
python3 tools/echel.py validate
```

## Operating Method

The working loop is:

```text
intent -> clarification -> product memory -> graph -> plan -> build packet -> implementation -> review -> readiness -> updated memory
```

Detailed method:

- [Operational Loop Methodology](development/method.md)
- [Product Graph](development/phase2-product-graph.md)
- [Agent Work Packets](development/phase3-agent-work-packets.md)
- [Product Cockpit](development/phase4-product-cockpit.md)
- [Readiness And Proof Packs](development/phase5-readiness-and-proof-packs.md)
