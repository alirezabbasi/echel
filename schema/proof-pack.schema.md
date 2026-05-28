---
type: schema
status: active
---
# Proof Pack Schema

Proof packs collect the evidence trail behind a readiness claim.

## File
- Path: `wiki/reports/proof-packs/{target}-proof-pack.md`
- Producer: `python3 tools/echel.py proof-pack --target <target>`

## Required Sections
- `Readiness`
- `Tasks`
- `Reviews`
- `Evidence Registry`
- `Graph Issues`
- `Readiness Issues`
- `Decisions`
- `Risks`
- `Verification Commands`

## Purpose
Proof packs make progress auditable by linking tasks, reviews, evidence, decisions, risks, and graph state into one durable report.

