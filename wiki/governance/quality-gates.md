---
type: governance
status: active
stage: governance-integrity
owner: Governance Auditor
---
# Quality Gates

## Purpose

Quality gates convert governance rules into executable or reviewable checkpoints. They stop lifecycle progress when product memory is missing, stale, contradictory, or unsupported by evidence.

## Gate Inventory

| Gate | Command | Blocks |
| --- | --- | --- |
| Wiki health | `make wiki-health` | Broken wiki links, governance validation failures, and wiki lint issues. |
| Graph validation | `python3 tools/echel.py graph validate` | Graph integrity, metadata, unresolved low-confidence assumptions, and structural graph issues. |
| Discovery readiness | `python3 tools/echel.py readiness --stage discovery` | Canon, strategy, requirements, and downstream generation from incomplete discovery. |
| Requirements readiness | `python3 tools/echel.py readiness --stage requirements` | Domain work from untestable or incomplete requirements. |
| Domain readiness | `python3 tools/echel.py readiness --stage domain` | Architecture work from weak domain language or coverage gaps. |
| Architecture readiness | `python3 tools/echel.py readiness --stage architecture` | Roadmap, execution task, and repository generation from incomplete architecture. |
| Release readiness | `python3 tools/echel.py readiness --stage release` | Production claims without validation, deployment, rollback, checklist, evidence, and risk coverage. |
| Doctor | `python3 tools/echel.py doctor` | Combined primitive validation, evidence, drift, and configured gates. |

## Gate Outcomes

| Outcome | Meaning |
| --- | --- |
| Pass | Downstream stage may proceed. |
| Blocked | Downstream stage must not proceed until blockers are fixed. |
| Accepted exception | Owner accepts risk in an ADR, risk record, or release/governance note. |
| Deferred | Work is explicitly out of scope and tracked as a future task or backlog item. |

## Exception Rules

- Exceptions must name the gate, blocker, owner, reason, mitigation, and expiry or review trigger.
- Exceptions that affect architecture, safety, release, or evidence require ADR or risk acceptance.
- Exceptions must not delete gate failures; they explain why downstream work can proceed despite known risk.

## Gate Maintenance

When a new lifecycle artifact, command, or graph node type is added, update the relevant gate documentation and add regression coverage if the behavior is executable.
