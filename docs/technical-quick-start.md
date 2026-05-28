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

## Graph And Memory Commands

```bash
python3 tools/echel.py graph build
python3 tools/echel.py graph validate
python3 tools/echel.py graph report
python3 tools/echel.py feature add --title "..."
python3 tools/echel.py risk add --title "..." --mitigation "..."
python3 tools/echel.py link --from <node-id> --to <node-id>
```

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

The cockpit includes dashboard, clarification queue, roadmap, work queue, architecture, graph, packets, reviews, readiness, risks, contradictions, agent activity, decisions, and chat.

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
