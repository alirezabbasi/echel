---
type: operations-sla-slo
stage: operations
status: draft
owner: operations-steward
updated: 2026-07-13
---
# SLA And SLO

## Purpose

This document defines the service expectations that operations, release, and product teams use to decide whether the product is healthy enough to operate and evolve.

## Source Inputs

- Non-functional requirements: [[../requirements/non-functional-requirements]]
- Observability: [[observability]]
- Incident response: [[incident-response]]
- Release plan: [[../roadmap/release-plan]]

## Service Level Objectives

| ID | Objective | User Outcome | Measurement | Target | Error Budget Policy | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SLO-001 | Release candidate verifies locally | Operators can trust the generated baseline before release. | `./scripts/verify.sh` result | 100% pass before release decision | Release pauses until failure is resolved or explicitly accepted. | QA Agent | Draft |
| SLO-002 | Health check responds | Support can confirm product baseline availability. | Health check execution result | Successful response after release handoff | Incident opened if health check fails. | Operations Steward | Draft |
| SLO-003 | Release readiness is auditable | Product owner sees blockers before production claim. | `readiness --stage release` output | Gate passes or blockers are documented | Production claim blocked while gate is unresolved. | Release Manager | Draft |
| SLO-004 | Evidence is registered | Verification proof survives agent context loss. | Evidence registry records | Required release evidence exists with checksum | Task or release closure blocked until evidence exists. | Governance Auditor | Draft |

## Service Level Agreements

| ID | Agreement | Audience | Commitment | Exclusion | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SLA-001 | Support response | Internal product owner and operators | Incidents are classified and assigned using [[incident-response]]. | External customer contractual SLA is out of scope until product-specific commitments exist. | Operations Steward | Draft |
| SLA-002 | Release support | Release Manager and Governance Auditor | Release decisions include validation, evidence, deployment, rollback, and operations artifacts. | Production environment-specific uptime commitments are future work. | Release Manager | Draft |

## Review Cadence

| ID | Cadence | Review Focus | Inputs | Output | Owner |
| --- | --- | --- | --- | --- | --- |
| SLO-REV-001 | Every release | SLO target adherence and accepted exceptions | Validation summary, release gate output, evidence registry | Release decision note | Release Manager |
| SLO-REV-002 | After incident | SLO miss, error budget impact, and follow-up | Incident record and observability signal | Evolution backlog item or risk update | Governance Auditor |
| SLO-REV-003 | Monthly | Whether SLOs still match product stage | NFRs, support history, roadmap | SLO update proposal | Product Manager |

## Quality Gate

- [ ] SLOs map to measurable commands or evidence.
- [ ] SLA commitments avoid unsupported external promises.
- [ ] Review cadence routes misses into governed product memory.
