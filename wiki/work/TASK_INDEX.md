---
type: task-index
status: active
stage: execution
---
# Execution Task Index

Generated from `wiki/execution/` phase artifacts by `python3 tools/echel.py execution-tasks`.

## Task Contract
- One source phase row becomes one agent-executable task.
- Generated tasks must stay small enough for one AI coding session.
- Each task carries objective, business reason, technical scope, files, dependencies, instructions, acceptance criteria, tests, validation, rollback, documentation updates, DoD, and out-of-scope.
- Repository factory work must consume these task records instead of roadmap prose.

## Tasks

| Task ID | Phase Task | Title | Source | Dependencies | Validation | Status |
| --- | --- | --- | --- | --- | --- | --- |
| [[TASK-1001-define-task-contract-source-map|TASK-1001]] | EP0-001 | Define task contract source map | `execution/phase-0-foundation.md` | RM-002, REQ-004, ARCH-205 | `make wiki-health` | Planned |
| [[TASK-1002-define-phase-handoff-rules|TASK-1002]] | EP0-002 | Define phase handoff rules | `execution/phase-0-foundation.md` | EP0-001 | `python3 tools/echel.py graph validate` | Planned |
| [[TASK-1003-preserve-gate-first-validation-baseline|TASK-1003]] | EP0-003 | Preserve gate-first validation baseline | `execution/phase-0-foundation.md` | GATE-REQUIREMENTS, GATE-DOMAIN, GATE-ARCHITECTURE | `python3 tools/echel.py readiness --stage architecture` | Planned |
| [[TASK-1004-generate-repository-skeleton|TASK-1004]] | EP1-001 | Generate repository skeleton | `execution/phase-1-mvp.md` | EP0-001, TASK-0023, TASK-0024 | `python3 tools/echel.py graph validate` | Planned |
| [[TASK-1005-add-local-development-docs|TASK-1005]] | EP1-002 | Add local development docs | `execution/phase-1-mvp.md` | EP1-001, TASK-0025 | `make wiki-health` | Planned |
| [[TASK-1006-verify-mvp-repository-baseline|TASK-1006]] | EP1-003 | Verify MVP repository baseline | `execution/phase-1-mvp.md` | EP1-001, EP1-002 | `python3 -m unittest discover -s tests` | Planned |
| [[TASK-1007-define-ai-agent-role-model|TASK-1007]] | EP2-001 | Define AI agent role model | `execution/phase-2-hardening.md` | TASK-0026 | `make wiki-health` | Planned |
| [[TASK-1008-add-lifecycle-playbooks-and-handoff-protocol|TASK-1008]] | EP2-002 | Add lifecycle playbooks and handoff protocol | `execution/phase-2-hardening.md` | EP2-001, TASK-0027, TASK-0028 | `make wiki-health` | Planned |
| [[TASK-1009-expand-graph-lifecycle-coverage|TASK-1009]] | EP2-003 | Expand graph lifecycle coverage | `execution/phase-2-hardening.md` | TASK-0029, TASK-0030 | `python3 tools/echel.py graph validate` | Planned |
| [[TASK-1010-generate-traceability-matrix|TASK-1010]] | EP2-004 | Generate traceability matrix | `execution/phase-2-hardening.md` | EP2-003, TASK-0031 | `python3 -m unittest discover -s tests` | Planned |
| [[TASK-1011-add-validation-artifacts|TASK-1011]] | EP3-001 | Add validation artifacts | `execution/phase-3-production.md` | TASK-0032, EP2-004 | `make wiki-health` | Planned |
| [[TASK-1012-add-validation-command|TASK-1012]] | EP3-002 | Add validation command | `execution/phase-3-production.md` | EP3-001, TASK-0033 | `python3 -m unittest discover -s tests` | Planned |
| [[TASK-1013-add-evidence-registration|TASK-1013]] | EP3-003 | Add evidence registration | `execution/phase-3-production.md` | EP3-002, TASK-0034 | `python3 tools/echel.py doctor` | Planned |
| [[TASK-1014-add-deployment-and-release-gates|TASK-1014]] | EP3-004 | Add deployment and release gates | `execution/phase-3-production.md` | TASK-0035, TASK-0036 | `python3 tools/echel.py doctor` | Planned |
| [[TASK-1015-add-operations-artifacts|TASK-1015]] | EP3-005 | Add operations artifacts | `execution/phase-3-production.md` | TASK-0037 | `make wiki-health` | Planned |
| [[TASK-1016-add-learning-loop|TASK-1016]] | EP4-001 | Add learning loop | `execution/phase-4-evolution.md` | TASK-0038, Phase 3 operations docs | `python3 -m unittest discover -s tests` | Planned |
| [[TASK-1017-redesign-cockpit-around-lifecycle|TASK-1017]] | EP4-002 | Redesign cockpit around lifecycle | `execution/phase-4-evolution.md` | TASK-0039, TASK-0040, EP4-001 | `make wiki-health` | Planned |
| [[TASK-1018-add-governance-integrity-artifacts|TASK-1018]] | EP4-003 | Add governance integrity artifacts | `execution/phase-4-evolution.md` | TASK-0041, TASK-0042, TASK-0043 | `python3 tools/echel.py doctor` | Planned |
| [[TASK-1019-preserve-migration-compatibility|TASK-1019]] | EP4-004 | Preserve migration compatibility | `execution/phase-4-evolution.md` | TASK-0044, TASK-0045, TASK-0046 | `make wiki-health` | Planned |
| [[TASK-1020-publish-vnext-proof-and-final-gate|TASK-1020]] | EP4-005 | Publish vNext proof and final gate | `execution/phase-4-evolution.md` | TASK-0047, TASK-0048, TASK-0049, TASK-0050 | `python3 tools/echel.py doctor` | Planned |
