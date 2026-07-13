---
type: governance
status: active
stage: governance-integrity
owner: Governance Auditor
---
# Repository Integrity Audit Model

## Purpose

The repository integrity audit defines what `python3 tools/echel.py integrity audit` reports and what the Governance Auditor reviews before later governance work proceeds.

## Audit Scope

| Area | Signals |
| --- | --- |
| Missing docs | Required lifecycle artifacts from `schema/lifecycle-stage.schema.md` and generated task requirements. |
| Stale docs | Deprecated markers, canon drift, superseded ADRs, stale generated sections, and old task statuses. |
| Broken traceability | Missing source IDs, broken chains in `wiki/reports/traceability-matrix.md`, and graph validation issues. |
| Missing ADRs | Architecture changes without accepted decision records. |
| Missing tests | Requirements, tasks, or architecture-critical behavior without validation mapping. |
| Missing evidence | Closed tasks, validation claims, or release claims without registry-backed evidence. |
| Methodology violations | Code before task packet, downstream work before gate pass, assumptions treated as facts, or unrecorded exceptions. |
| Contradictions | Conflicting product memory, stale canon, unresolved risk, or incompatible architecture statements. |
| Migration compatibility | Root product-memory pages missing lifecycle compatibility references or old links broken during vNext adoption. |

## Manual Audit Commands

```bash
make wiki-health
python3 tools/echel.py graph validate
python3 tools/echel.py traceability
python3 tools/echel.py contradictions sync
python3 tools/echel.py migration compatibility
python3 tools/echel.py validate
python3 tools/echel.py readiness --stage release
python3 tools/echel.py doctor
```

## Audit Finding Format

| Field | Meaning |
| --- | --- |
| Finding ID | Stable audit row ID, such as `AUD-001`. |
| Severity | `critical`, `major`, `minor`, or `info`. |
| Area | Missing docs, stale docs, traceability, ADR, tests, evidence, methodology, or contradiction. |
| Source | Artifact, command, report, or gate that exposed the issue. |
| Impact | Why the issue matters to AI-assisted delivery. |
| Required action | Fix, accepted exception, contradiction record, task, ADR, or risk. |
| Owner | Accountable lifecycle role. |
| Status | Open, accepted, deferred, resolved. |

## Current Audit Baseline

| Finding ID | Severity | Area | Source | Impact | Required Action | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AUD-001 | critical | Discovery | `GATE-DISCOVERY` | Discovery still contains template gaps, so early-stage product truth is not complete. | Complete PDS fields or keep downstream use explicitly governed. | Founder Interviewer | Open |
| AUD-002 | critical | Release evidence | `GATE-RELEASE` | Production release cannot be claimed without checklist and evidence coverage. | Register evidence and complete or accept production checklist rows. | Release Manager | Open |
| AUD-003 | major | Traceability | `wiki/reports/traceability-matrix.md` | Canon/evidence graph links are not yet complete. | Add graph-backed canon statement links and evidence coverage in future traceability work. | Governance Auditor | Open |

## Command Contract

`python3 tools/echel.py integrity audit` should read the same governance model and report:

- missing docs
- stale docs
- broken traceability
- missing ADRs
- missing tests
- missing evidence
- methodology violations
- contradictions

The command writes a durable report to `wiki/reports/repository-integrity-audit.md` and returns non-zero for critical unresolved findings unless accepted exceptions are recorded.

Contradiction findings are read from `wiki/governance/contradictions.md`. Refresh that register with `python3 tools/echel.py contradictions sync` before the audit when local memory records may contain new contradictions.

Migration compatibility is recorded in `wiki/governance/migration-compatibility.md`. Refresh it with `python3 tools/echel.py migration compatibility` before changing initialization or moving root wiki pages.
